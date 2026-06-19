"""博客蓝图（SEO 内容站）"""
from flask import Blueprint

blog_bp = Blueprint('blog', __name__, template_folder='../templates')
