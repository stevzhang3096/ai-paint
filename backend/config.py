"""配置管理"""
import os

# 智谱 API Key（服务器端用，不暴露给用户）
ZHIPU_API_KEY = "fc7e1baf04774595a5f038854646c61c.QGZw8VuctAKut8Gf"

# MySQL 配置
MYSQL_CONFIG = {
    "host": "172.17.0.3",
    "port": 3306,
    "user": "paint",
    "password": "paint123",
    "database": "ai_paint",
    "charset": "utf8mb4",
}

# DB_PATH 保留兼容（不再使用）
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'paint.db')

# 可选用的画图模型
IMAGE_MODELS = {
    "glm-image": {
        "name": "GLM-Image (HD)",
        "name_cn": "GLM-Image (高清)",
        "provider": "zhipu",
        "default": True,
    },
    "cogview-4": {
        "name": "CogView-4 (Standard)",
        "name_cn": "CogView-4 (标准)",
        "provider": "zhipu",
        "default": False,
    },
}

# 可选的图片尺寸（带中文标签描述）
IMAGE_SIZES = [
    {"value": "1024x1024", "label": "1024x1024 (Square)", "label_cn": "1024×1024 (方形)"},
    {"value": "1280x1280", "label": "1280x1280 (Square)", "label_cn": "1280×1280 (方形)"},
    {"value": "1440x1440", "label": "1440x1440 (Square)", "label_cn": "1440×1440 (方形)"},
    {"value": "1568x1056", "label": "1568x1056 (Landscape)", "label_cn": "1568×1056 (横版)"},
    {"value": "1056x1568", "label": "1056x1568 (Portrait)", "label_cn": "1056×1568 (竖版)"},
    {"value": "1472x1088", "label": "1472x1088 (Landscape)", "label_cn": "1472×1088 (横版)"},
    {"value": "1088x1472", "label": "1088x1472 (Portrait)", "label_cn": "1088×1472 (竖版)"},
    {"value": "1728x960", "label": "1728x960 (Ultrawide)", "label_cn": "1728×960 (超宽)"},
]

# 新用户免费额度
FREE_CREDITS = 10

# USDT 套餐（额度单位是张数）
PLANS = {
    "starter":   {"usdt": 5,   "credits": 50,   "desc": "经济包 — 50张"},
    "popular":   {"usdt": 15,  "credits": 200,  "desc": "热门包 — 200张 ✅"},
    "pro":       {"usdt": 40,  "credits": 600,  "desc": "专业包 — 600张"},
}

# ── 邮件配置（找回密码用） ──
# 使用 QQ 邮箱 SMTP，需开启 SMTP 服务并获取授权码
MAIL_CONFIG = {
    "server": "smtp.qq.com",
    "port": 587,
    "use_tls": True,
    "username": "your_email@qq.com",      # 替换成你的 QQ 邮箱
    "password": "your_smtp_authorization_code",  # SMTP 授权码（不是登录密码）
    "sender": "your_email@qq.com",
}

# 验证码有效期（分钟）
VERIFY_CODE_EXPIRE_MINUTES = 10

# LemonSqueezy Webhook Secret（在 LS 后台 Settings → Webhooks 里设置）
# 留空则不验证签名（仅开发测试用）
LEMON_SQUEEZY_WEBHOOK_SECRET = ""

# 服务器端口
PORT = 5001
