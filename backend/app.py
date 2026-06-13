"""Flask 主应用 — 无需 API Key，注册登录后 session 鉴权 + Flask-Admin 后台"""
import sys
import os
import random
import datetime
sys.path.insert(0, os.path.dirname(__file__))
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import config
import db
from ai_api import generate_image
import requests
import uuid

# ── Flask-Mail ──
from flask_mail import Mail, Message
mail = Mail()
# ── Flask-Admin ──
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, static_folder=None)
app.secret_key = "da6cc55e429b73bd6197cc63d8fe314f625321267789b8dd"
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
CORS(app, supports_credentials=True)
# ── 初始化数据库 ──
db.init_db()
# ── SQLAlchemy（Flask-Admin 需要） ──
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f"mysql+pymysql://{config.MYSQL_CONFIG['user']}:{config.MYSQL_CONFIG['password']}@" \
    f"{config.MYSQL_CONFIG['host']}:{config.MYSQL_CONFIG['port']}/{config.MYSQL_CONFIG['database']}?charset={config.MYSQL_CONFIG['charset']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_sa = SQLAlchemy(app)
# ── SQLAlchemy 模型 ──
class UserModel(db_sa.Model):
    __tablename__ = 'users'
    id = db_sa.Column(db_sa.Integer, primary_key=True)
    email = db_sa.Column(db_sa.String(255), unique=True, nullable=False)
    password = db_sa.Column(db_sa.String(255), nullable=False)
    credits = db_sa.Column(db_sa.Integer, default=0)
    role = db_sa.Column(db_sa.SmallInteger, default=0)
    created_at = db_sa.Column(db_sa.DateTime)
class GenerationModel(db_sa.Model):
    __tablename__ = 'generations'
    id = db_sa.Column(db_sa.Integer, primary_key=True)
    user_id = db_sa.Column(db_sa.Integer)
    prompt = db_sa.Column(db_sa.Text)
    model = db_sa.Column(db_sa.String(50))
    size = db_sa.Column(db_sa.String(20))
    image_url = db_sa.Column(db_sa.Text)
    created_at = db_sa.Column(db_sa.DateTime)
    def user_email(self):
        u = db.get_user(self.user_id)
        return u['email'] if u else str(self.user_id)
    user_email.short_description = '用户'
class OrderModel(db_sa.Model):
    __tablename__ = 'orders'
    id = db_sa.Column(db_sa.Integer, primary_key=True)
    user_id = db_sa.Column(db_sa.Integer)
    txid = db_sa.Column(db_sa.String(255), unique=True)
    usdt_amount = db_sa.Column(db_sa.Numeric(10, 2))
    plan_name = db_sa.Column(db_sa.String(50))
    credits = db_sa.Column(db_sa.Integer)
    status = db_sa.Column(db_sa.String(20), default='pending')
    created_at = db_sa.Column(db_sa.DateTime)
    def user_email(self):
        u = db.get_user(self.user_id)
        return u['email'] if u else str(self.user_id)
    user_email.short_description = '用户'
# ── 自定义 Admin Index ──
class AdminAuthMixin:
    def is_accessible(self):
        user_id = session.get('user_id')
        if not user_id:
            return False
        user = db.get_user(user_id)
        return user and user.get('role') == 1
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/admin/login')
class SecureAdminIndexView(AdminAuthMixin, AdminIndexView):
    @expose('/')
    def index(self):
        if not self.is_accessible():
            return redirect('/admin/login')
        # 统计数据传给模板
        self._template_args['admin_stats'] = db.get_admin_stats()
        return super().index()
class SecureModelView(AdminAuthMixin, ModelView):
    can_delete = True
    can_create = True
    can_edit = True
    page_size = 20
# ── 具体视图配置 ──
class UserAdmin(SecureModelView):
    column_list = ['id', 'email', 'credits', 'role', 'created_at']
    column_searchable_list = ['email']
    column_filters = ['role', 'credits']
    form_excluded_columns = ['password']
    # 不可通过后台修改密码
    column_labels = dict(email='邮箱', credits='额度', role='角色', created_at='注册时间')
    def on_model_change(self, form, model, is_created):
        # 防止通过后台绕过密码
        pass
class GenerationAdmin(SecureModelView):
    column_list = ['id', 'user_email', 'prompt', 'model', 'size', 'created_at']
    column_searchable_list = ['prompt']
    column_filters = ['model', 'size', 'created_at']
    can_create = False
    can_edit = False
    column_labels = dict(user_email='用户', prompt='提示词', model='模型', size='尺寸', created_at='生成时间')
    column_formatters = {
        'user_email': lambda v, c, m, p: m.user_email() if hasattr(m, 'user_email') else str(m.user_id)
    }

class OrderAdmin(SecureModelView):
    column_list = ['id', 'user_email', 'txid', 'usdt_amount', 'plan_name', 'credits', 'status', 'created_at']
    column_searchable_list = ['txid']
    column_filters = ['status', 'plan_name']
    can_create = False
    can_edit = True
    column_labels = dict(
        user_email='用户', txid='交易ID', usdt_amount='USDT金额', plan_name='套餐',
        credits='额度', status='状态', created_at='时间'
    )
    column_formatters = {
        'user_email': lambda v, c, m, p: m.user_email() if hasattr(m, 'user_email') else str(m.user_id)
    }

class PlanModel(db_sa.Model):
    __tablename__ = 'plans'
    id = db_sa.Column(db_sa.Integer, primary_key=True)
    name = db_sa.Column(db_sa.String(50), unique=True)
    usdt = db_sa.Column(db_sa.Numeric(10, 2))
    credits = db_sa.Column(db_sa.Integer)
    description = db_sa.Column(db_sa.String(200), default='')
    is_popular = db_sa.Column(db_sa.SmallInteger, default=0)
    is_active = db_sa.Column(db_sa.SmallInteger, default=1)
    sort_order = db_sa.Column(db_sa.Integer, default=0)
    created_at = db_sa.Column(db_sa.DateTime)
    updated_at = db_sa.Column(db_sa.DateTime)

class PlanAdmin(SecureModelView):
    column_list = ['name', 'usdt', 'credits', 'description', 'is_popular', 'is_active', 'sort_order']
    column_searchable_list = ['name']
    column_filters = ['is_active', 'is_popular']
    can_create = True
    can_edit = True
    can_delete = True
    column_labels = dict(
        name='套餐名', usdt='USDT价格', credits='额度(张)',
        description='描述', is_popular='热门', is_active='启用',
        sort_order='排序', created_at='创建时间', updated_at='更新时间'
    )
    form_choices = {
        'is_popular': [
            (0, '否'),
            (1, '是'),
        ],
        'is_active': [
            (0, '禁用'),
            (1, '启用'),
        ],
    }
    column_formatters = {
        'is_popular': lambda v, c, m, p: '\u2705' if m.is_popular else '',
        'is_active': lambda v, c, m, p: '\u2705' if m.is_active else '\u274c',
    }

# ── 内置验证码存储（内存，重启清空） ──
verify_codes = {}  # email -> {"code": "123456", "expires_at": datetime}

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """发送重置密码验证码到用户邮箱"""
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()

    if not email or '@' not in email:
        return jsonify({"error": "请输入有效邮箱"}), 400

    user = db.get_user_by_email(email)
    if not user:
        # 不暴露邮箱是否存在，统一返回成功
        return jsonify({"success": True, "message": "如果该邮箱已注册，验证码已发送"})

    # 生成 6 位验证码
    code = ''.join(random.choices('0123456789', k=6))
    now = datetime.datetime.now()
    expire = now + datetime.timedelta(minutes=config.VERIFY_CODE_EXPIRE_MINUTES)
    verify_codes[email] = {"code": code, "expires_at": expire}

    # 发送邮件
    try:
        msg = Message(
            subject="AiCanvas - 密码重置验证码",
            sender=config.MAIL_CONFIG["sender"],
            recipients=[email],
            body=f"您的验证码是：{code}\n\n验证码 {config.VERIFY_CODE_EXPIRE_MINUTES} 分钟内有效。\n如果不是您本人操作，请忽略此邮件。\n\n—— AiCanvas 图片生成"
        )
        mail.send(msg)
        print(f"[MAIL] ✅ 验证码已发送到 {email}", flush=True)
        return jsonify({"success": True, "message": "验证码已发送到您的邮箱"})
    except Exception as e:
        print(f"[MAIL] ❌ 发送失败 {email}: {e}", flush=True)
        # 调试模式下返回验证码（方便本地测试）
        if app.debug:
            return jsonify({"success": True, "message": f"[DEBUG] 验证码：{code}"})
        return jsonify({"error": "邮件发送失败，请稍后重试或联系管理员"}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """验证码校验 + 重置密码"""
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    code = (data.get('code') or '').strip()
    new_password = data.get('new_password') or ''

    if not email or not code or not new_password:
        return jsonify({"error": "请填写完整信息"}), 400
    if len(new_password) < 4:
        return jsonify({"error": "密码至少 4 位"}), 400

    record = verify_codes.get(email)
    if not record:
        return jsonify({"error": "请先获取验证码"}), 400

    now = datetime.datetime.now()
    if now > record["expires_at"]:
        verify_codes.pop(email, None)
        return jsonify({"error": "验证码已过期，请重新获取"}), 400

    if record["code"] != code:
        return jsonify({"error": "验证码错误"}), 400

    # 重置密码
    import hashlib
    pw_hash = hashlib.sha256(new_password.encode()).hexdigest()
    db.update_password(email, pw_hash)

    verify_codes.pop(email, None)
    return jsonify({"success": True, "message": "密码重置成功，请重新登录"})

# ── 初始化 Admin ──
# ── 初始化 Mail ──
app.config['MAIL_SERVER'] = config.MAIL_CONFIG['server']
app.config['MAIL_PORT'] = config.MAIL_CONFIG['port']
app.config['MAIL_USE_TLS'] = config.MAIL_CONFIG['use_tls']
app.config['MAIL_USERNAME'] = config.MAIL_CONFIG['username']
app.config['MAIL_PASSWORD'] = config.MAIL_CONFIG['password']
mail.init_app(app)

admin = Admin(app, name='AiCanvas 管理后台', index_view=SecureAdminIndexView())
admin.add_view(UserAdmin(UserModel, db_sa, name='用户管理'))
admin.add_view(GenerationAdmin(GenerationModel, db_sa, name='生成记录'))
admin.add_view(OrderAdmin(OrderModel, db_sa, name='充值订单'))
admin.add_view(PlanAdmin(PlanModel, db_sa, name='套餐管理'))
# ── Admin 后台登录页 ──
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = db.verify_login(email, password)
        if user and user.get('role') == 1:
            session['user_id'] = user['id']
            return redirect('/admin')
        return '''
            <!DOCTYPE html><html><head><meta charset="utf-8">
            <title>管理员登录 - AiCanvas</title>
            <style>
                body{background:#0f1117;color:#e4e6ed;font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
                .box{background:#1a1c25;border:1px solid #2a2d3a;border-radius:16px;padding:40px;width:360px}
                h1{text-align:center;color:#8b5cf6;margin-bottom:24px;font-size:20px}
                input{width:100%;padding:12px;margin-bottom:12px;background:#13151d;border:1px solid #2a2d3a;border-radius:10px;color:#e4e6ed;font-size:14px;box-sizing:border-box}
                button{width:100%;padding:12px;border-radius:10px;border:none;background:#8b5cf6;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
                .error{color:#f87171;font-size:13px;text-align:center;margin-bottom:8px}
                .help{text-align:center;margin-top:12px;font-size:12px;color:#6b7280}
            </style></head><body>
            <div class="box">
                <h1>🔐 管理员登录</h1>
                <div class="error">邮箱或密码错误，或非管理员账号</div>
                <form method="post">
                    <input type="email" name="email" placeholder="管理员邮箱" value="''' + email + '''" required>
                    <input type="password" name="password" placeholder="密码" required>
                    <button type="submit">登录</button>
                </form>
                <div class="help">仅限 role=1 的管理员账号登录</div>
            </div></body></html>
        '''
    return '''
        <!DOCTYPE html><html><head><meta charset="utf-8">
        <title>管理员登录 - AiCanvas</title>
        <style>
            body{background:#0f1117;color:#e4e6ed;font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
            .box{background:#1a1c25;border:1px solid #2a2d3a;border-radius:16px;padding:40px;width:360px}
            h1{text-align:center;color:#8b5cf6;margin-bottom:24px;font-size:20px}
            input{width:100%;padding:12px;margin-bottom:12px;background:#13151d;border:1px solid #2a2d3a;border-radius:10px;color:#e4e6ed;font-size:14px;box-sizing:border-box}
            button{width:100%;padding:12px;border-radius:10px;border:none;background:#8b5cf6;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
            .help{text-align:center;margin-top:12px;font-size:12px;color:#6b7280}
        </style></head><body>
        <div class="box">
            <h1>🔐 管理员登录</h1>
            <form method="post">
                <input type="email" name="email" placeholder="管理员邮箱" required>
                <input type="password" name="password" placeholder="密码" required>
                <button type="submit">登录</button>
            </form>
            <div class="help">仅限 role=1 的管理员账号登录</div>
        </div></body></html>
    '''
@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    return redirect('/admin/login')
# ── 前端路由 ──
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)
# ── 用户认证 API ──
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    if not email or not password:
        return jsonify({"error": "邮箱和密码不能为空"}), 400
    import re
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "邮箱格式不正确"}), 400
    user = db.create_user(email, password)
    if not user:
        return jsonify({"error": "邮箱已注册"}), 409
    db.add_credits(user["id"], config.FREE_CREDITS)
    session['user_id'] = user["id"]
    return jsonify({
        "success": True,
        "user": {"id": user["id"], "email": user["email"], "credits": config.FREE_CREDITS}
    })
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = db.verify_login(data.get('email', ''), data.get('password', ''))
    if not user:
        return jsonify({"error": "邮箱或密码错误"}), 401
    session['user_id'] = user["id"]
    return jsonify({
        "success": True,
        "user": {"id": user["id"], "email": user["email"], "credits": user["credits"]}
    })
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True})

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """修改密码（需已登录）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "请先登录"}), 401
    data = request.get_json()
    old_pwd = (data.get('old_password') or '').strip()
    new_pwd = (data.get('new_password') or '').strip()
    if not old_pwd or not new_pwd:
        return jsonify({"error": "请填写完整"}), 400
    if len(new_pwd) < 4:
        return jsonify({"error": "新密码至少 4 位"}), 400
    user = db.get_user(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    import hashlib
    old_hash = hashlib.sha256(old_pwd.encode()).hexdigest()
    if user["password"] != old_hash:
        return jsonify({"error": "当前密码错误"}), 403
    new_hash = hashlib.sha256(new_pwd.encode()).hexdigest()
    db.update_password(user["email"], new_hash)
    return jsonify({"success": True, "message": "密码修改成功"})

@app.route('/api/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"user": None}), 200
    user = db.get_user(user_id)
    if not user:
        session.pop('user_id', None)
        return jsonify({"user": None}), 200
    return jsonify({"user": user})
# ── 图片生成 ──
@app.route('/api/models', methods=['GET'])
def list_models():
    models = {k: {"name": v["name"], "default": v["default"]}
              for k, v in config.IMAGE_MODELS.items()}
    return jsonify({"models": models, "sizes": config.IMAGE_SIZES})
@app.route('/api/generate', methods=['POST'])
def generate():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "请先登录"}), 401
    data = request.get_json()
    prompt = (data or {}).get('prompt', '').strip()
    model = (data or {}).get('model', 'glm-image')
    size = (data or {}).get('size', '1280x1280')
    if not prompt:
        return jsonify({"error": "prompt 不能为空"}), 400
    if len(prompt) > 500:
        return jsonify({"error": "prompt 最长 500 字符"}), 400
    valid_sizes = [s["value"] if isinstance(s, dict) else s for s in config.IMAGE_SIZES]
    if size not in valid_sizes:
        return jsonify({"error": f"不支持的尺寸: {size}"}), 400
    credits = db.get_user_credits(user_id)
    if credits < 1:
        return jsonify({"error": "额度不足，请充值"}), 402
    result = generate_image(prompt, size, model)
    if not result["success"]:
        return jsonify({"error": result["error"]}), 502
    # 下载图片到本地
    local_filename = None
    try:
        img_resp = requests.get(result["image_url"], timeout=15)
        if img_resp.status_code == 200:
            ext = ".png"
            local_filename = f"{uuid.uuid4().hex}{ext}"
            img_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')
            os.makedirs(img_dir, exist_ok=True)
            with open(os.path.join(img_dir, local_filename), 'wb') as f:
                f.write(img_resp.content)
    except Exception as e:
        print(f"[IMG] 下载图片失败: {e}", flush=True)

    db.deduct_credit(user_id)
    gen_id = db.save_generation(user_id, prompt, model, size, result["image_url"], local_filename)
    image_url = f"/api/image/{gen_id}" if local_filename else result["image_url"]
    return jsonify({
        "success": True,
        "gen_id": gen_id,
        "image_url": image_url,
        "credits_left": db.get_user_credits(user_id)
    })

@app.route('/api/image/<int:gen_id>')
def serve_image(gen_id):
    """本地图片代理 — 解决智谱图片跨域/过期问题"""
    gen = db.get_generation(gen_id)
    if not gen:
        return "图片不存在", 404
    # 优先返回本地缓存
    if gen.get("local_file"):
        img_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')
        filepath = os.path.join(img_dir, gen["local_file"])
        if os.path.exists(filepath):
            return send_from_directory(img_dir, gen["local_file"])
    # 没有本地文件，直接302到原图
    return redirect(gen["image_url"])

@app.route('/api/history', methods=['GET'])
def get_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "请先登录"}), 401
    gens = db.get_user_generations(user_id)
    # 把 image_url 转成本地代理
    for g in gens:
        if g.get("local_file"):
            g["image_url"] = f"/api/image/{g['id']}"
    return jsonify({"generations": gens})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """获取当前用户的充值记录"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "请先登录"}), 401
    orders = db.get_user_orders(user_id)
    return jsonify({"orders": orders})

@app.route('/api/plans', methods=['GET'])
def get_plans():
    plans = db.get_plans()
    result = {}
    for p in plans:
        result[p["name"]] = {
            "usdt": float(p["usdt"]),
            "credits": p["credits"],
            "desc": p["description"],
            "popular": bool(p["is_popular"]),
        }
    return jsonify({"plans": result})
# ── USDT 充值回调 ──
@app.route('/api/recharge/notify', methods=['POST'])
def recharge_notify():
    data = request.get_json()
    user_id = data.get('user_id')
    txid = data.get('txid')
    usdt_amount = data.get('usdt_amount')
    plan_name = data.get('plan_name')
    plan = db.get_plan_by_name(plan_name)
    if not plan:
        return jsonify({"error": "无效套餐"}), 400
    if abs(usdt_amount - plan["usdt"]) > 0.01:
        return jsonify({"error": "金额不匹配"}), 400
    db.create_order(user_id, txid, usdt_amount, plan_name, plan["credits"])
    db.confirm_order(txid)
    return jsonify({"success": True, "credits_added": plan["credits"]})


# ── USDT TRC-20 自动验证 ──
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
USDT_ADDRESS = "TQ5dyshgSMrBxbuQMvSbfTqconC7Cze2q7"

@app.route('/api/usdt/check', methods=['POST'])
def usdt_check_payment():
    """
    用户填入 TxID 后验证：
    1. 查 TronScan 确认该 TxID 是否是一笔到收款地址的 USDT 转账
    2. 匹配到账金额 → 自动加额度
    3. 记录已处理的 TxID 防重复
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "请先登录"}), 401

    data = request.get_json() or {}
    txid = (data.get('txid') or '').strip()

    if not txid:
        return jsonify({"error": "请输入交易哈希 (TxID)"}), 400

    # 查是否已处理过
    if db.is_tx_processed(txid):
        return jsonify({"error": "此交易已被处理过"}), 400

    try:
        # 直接查指定 TxID 的交易详情
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        url = f"https://api.trongrid.io/v1/transactions/{txid}/events?limit=10"
        resp = requests.get(url, headers=headers, timeout=15)

        # 也可以通过 TRC20 转账记录查
        # 用 query account TRC20 transfers by txid
        url2 = f"https://api.trongrid.io/v1/accounts/{USDT_ADDRESS}/transactions/trc20"
        params2 = {"limit": 20, "only_to": True, "only_confirmed": True}
        resp2 = requests.get(url2, headers=headers, params=params2, timeout=15)

        if resp2.status_code != 200:
            return jsonify({"error": "TronScan 查询失败", "retryable": True}), 502

        transfers = resp2.json().get("data", [])

        # 找匹配 TxID 的转账
        matched_tx = None
        for t in transfers:
            if t.get("transaction_id", "") == txid:
                matched_tx = t
                break

        if not matched_tx:
            return jsonify({"found": False, "message": "未找到该交易，请确认 TxID 正确且已确认"})

        # 验证是 USDT 且到收款地址
        token_info = matched_tx.get("token_info", {}) or {}
        contract = (token_info.get("address") or "").lower()

        if contract != USDT_CONTRACT.lower():
            return jsonify({"error": "此交易不是 USDT 转账"}), 400

        # 解析金额
        decimals = token_info.get("decimals", 6)
        value_str = matched_tx.get("value", "0")
        amount = int(value_str) / (10 ** decimals)

        if amount < 1:
            return jsonify({"error": f"金额 ${amount:.2f} 低于最低 $1"}), 400

        # 匹配套餐
        plans = db.get_plans()
        matched_plan = None
        for p in plans:
            if abs(float(p['usdt']) - amount) < 0.5:
                matched_plan = p
                break

        if matched_plan:
            credits_to_add = matched_plan['credits']
            plan_name = matched_plan['name']
        else:
            # 按量：1 USDT ≈ 40 张
            credits_to_add = int(amount * 40)
            plan_name = f"按量充值 ${amount:.2f}"

        # 加额度 + 记录
        db.add_credits(user_id, credits_to_add)
        db.create_order(user_id, txid, amount, plan_name, credits_to_add)
        db.confirm_order(txid)
        db.save_processed_tx(txid, user_id, amount, credits_to_add)

        print(f"[USDT] ✅ 用户 {user_id} 充值 ${amount:.2f} → +{credits_to_add}张 (tx:{txid[:16]}...)", flush=True)

        return jsonify({
            "found": True,
            "usdt_amount": amount,
            "plan_name": plan_name,
            "credits_added": credits_to_add,
            "txid": txid[:16] + "...",
            "credits_left": db.get_user_credits(user_id)
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "TronScan 查询超时，请重试", "retryable": True}), 502
    except Exception as e:
        print(f"[USDT] ❌ 验证异常: {e}", flush=True)
        return jsonify({"error": "验证失败，请稍后重试", "retryable": True}), 500

# ── LemonSqueezy Webhook ──
@app.route('/api/ls-webhook', methods=['POST'])
def ls_webhook():
    """接收 LemonSqueezy 支付成功回调"""
    import hashlib, hmac

    # 验证签名（LS 用 Secret 签名）
    secret = config.LEMON_SQUEEZY_WEBHOOK_SECRET.encode()
    signature = request.headers.get('X-Signature', '')

    # LS 的签名是 HMAC-SHA256 的 hex 字符串
    payload = request.get_data()
    expected_sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    # 有 secret 时才验证签名（没配就先跳过验证）
    if config.LEMON_SQUEEZY_WEBHOOK_SECRET and signature != expected_sig:
        print(f"[LS] ⚠️ 签名验证失败: {signature[:20]}... != {expected_sig[:20]}...", flush=True)
        return jsonify({"error": "invalid signature"}), 401

    data = request.get_json()
    if not data or data.get('meta', {}).get('event_name') != 'order_created':
        # 只处理 order_created 事件
        return jsonify({"ok": True})

    try:
        attrs = data.get('data', {}).get('attributes', {})
        customer_email = attrs.get('user_email', '').lower()
        variant_name = attrs.get('variant_name', '')
        order_id = attrs.get('order_id', 0)
        total_usd = float(attrs.get('total', 0))

        if not customer_email or not variant_name:
            print(f"[LS] ⚠️ 缺少必要字段: email={customer_email}, variant={variant_name}", flush=True)
            return jsonify({"ok": True})

        # 查找用户（通过 email）
        user = db.get_user_by_email(customer_email)
        if not user:
            # 用户不存在，尝试注册一个
            import hashlib as hl
            import secrets
            temp_pwd = secrets.token_hex(8)
            user = db.create_user(customer_email, temp_pwd)
            if not user:
                print(f"[LS] ⚠️ 无法为用户创建账号: {customer_email}", flush=True)
                return jsonify({"ok": True})
            print(f"[LS] 为新用户创建账号: {customer_email}", flush=True)

        # 匹配套餐
        plans = db.get_plans()
        matched_plan = None
        for p in plans:
            # 根据 variant_name 匹配套餐名，或按金额匹配
            if p['name'].lower() in variant_name.lower() or abs(float(p['usdt']) - total_usd) < 1:
                matched_plan = p
                break

        if not matched_plan and plans:
            # 兜底：用第一个套餐
            matched_plan = plans[0]

        if matched_plan:
            credits_to_add = matched_plan['credits']
            db.add_credits(user['id'], credits_to_add)
            db.create_order(user['id'], f"ls_{order_id}", total_usd, matched_plan['name'], credits_to_add)
            db.confirm_order(f"ls_{order_id}")
            print(f"[LS] ✅ {customer_email} 充值成功: {matched_plan['name']} (+{credits_to_add}张)", flush=True)
        else:
            # 没有匹配套餐，按 $1 = 10 张给
            credits_to_add = int(total_usd * 10)
            db.add_credits(user['id'], credits_to_add)
            db.create_order(user['id'], f"ls_{order_id}", total_usd, "按量充值", credits_to_add)
            db.confirm_order(f"ls_{order_id}")
            print(f"[LS] ✅ {customer_email} 按量充值: ${total_usd} (+{credits_to_add}张)", flush=True)

    except Exception as e:
        print(f"[LS] ❌ webhook 处理异常: {e}", flush=True)

    return jsonify({"ok": True})

# ── 启动 ──
if __name__ == '__main__':
    print(f"🚀 AI Paint 启动中 → http://0.0.0.0:{config.PORT}")
    print(f"📦 数据库: MySQL ({config.MYSQL_CONFIG['host']}:{config.MYSQL_CONFIG['port']}/{config.MYSQL_CONFIG['database']})")
    print(f"🔐 管理后台: http://localhost:{config.PORT}/admin/")
    app.run(host='0.0.0.0', port=config.PORT, debug=True)
