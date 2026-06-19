"""博客蓝图（SEO 内容站）"""
from flask import Blueprint

blog_bp = Blueprint('blog', __name__, template_folder='../templates')

# ── 注册路由（确保装饰器执行） ──
import blog.routes  # noqa: F401
