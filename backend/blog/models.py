"""博客文章数据库操作"""
import datetime
import re
import pymysql
from pymysql.cursors import DictCursor
from config import MYSQL_CONFIG


def get_blog_conn():
    return pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset=MYSQL_CONFIG["charset"],
        cursorclass=DictCursor,
    )


def init_blog_table():
    """初始化博客文章表"""
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blog_posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    slug VARCHAR(255) NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    excerpt VARCHAR(500) DEFAULT '',
                    meta_description VARCHAR(300) DEFAULT '',
                    meta_keywords VARCHAR(300) DEFAULT '',
                    author VARCHAR(100) DEFAULT 'AiCanvas',
                    published BOOLEAN DEFAULT FALSE,
                    published_at DATETIME DEFAULT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_slug (slug),
                    INDEX idx_published (published, published_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
        conn.commit()
    finally:
        conn.close()


def slugify(text):
    """将文本转为 URL 友好的 slug"""
    slug = text.lower()
    # 替换非字母数字和中文的字符为短横
    slug = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    # 限制长度
    return slug[:200]


def create_post(title, content, excerpt="", meta_description="", meta_keywords="", author="AiCanvas"):
    """创建文章，自动生成 slug"""
    slug = slugify(title)
    # 处理重复 slug
    existing = get_post_by_slug(slug)
    if existing:
        slug = f"{slug}-{int(datetime.datetime.now().timestamp())}"

    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO blog_posts
                   (title, slug, content, excerpt, meta_description, meta_keywords, author)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (title, slug, content, excerpt[:500], meta_description[:300],
                 meta_keywords[:300], author),
            )
        conn.commit()
        return slug
    except pymysql.IntegrityError:
        # slug 冲突
        slug = f"{slug}-{int(datetime.datetime.now().timestamp())}"
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO blog_posts
                   (title, slug, content, excerpt, meta_description, meta_keywords, author)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (title, slug, content, excerpt[:500], meta_description[:300],
                 meta_keywords[:300], author),
            )
        conn.commit()
        return slug
    finally:
        conn.close()


def get_post_by_slug(slug):
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM blog_posts WHERE slug=%s", (slug,))
            return cur.fetchone()
    finally:
        conn.close()


def get_post_by_id(post_id):
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM blog_posts WHERE id=%s", (post_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_published_posts(page=1, per_page=10):
    """获取已发布的文章，按时间倒序"""
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            offset = (page - 1) * per_page
            cur.execute(
                """SELECT id, title, slug, excerpt, meta_description, author,
                          published_at, created_at
                   FROM blog_posts
                   WHERE published=TRUE AND published_at IS NOT NULL
                   ORDER BY published_at DESC
                   LIMIT %s OFFSET %s""",
                (per_page, offset),
            )
            posts = cur.fetchall()

            cur.execute(
                "SELECT COUNT(*) as cnt FROM blog_posts WHERE published=TRUE AND published_at IS NOT NULL"
            )
            total = cur.fetchone()["cnt"]
        return posts, total
    finally:
        conn.close()


def publish_post(post_id):
    """发布文章（设置 published=TRUE 和发布时间）"""
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE blog_posts
                   SET published=TRUE, published_at=COALESCE(published_at, NOW())
                   WHERE id=%s""",
                (post_id,),
            )
        conn.commit()
    finally:
        conn.close()


def get_all_published_posts():
    """获取所有已发布文章（用于 sitemap/RSS）"""
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, title, slug, published_at, updated_at
                   FROM blog_posts
                   WHERE published=TRUE AND published_at IS NOT NULL
                   ORDER BY published_at DESC"""
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_unpublished_posts(limit=50):
    """获取未发布的文章（自动发布脚本用）"""
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM blog_posts
                   WHERE published=FALSE
                   ORDER BY created_at ASC
                   LIMIT %s""",
                (limit,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def count_posts():
    conn = get_blog_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM blog_posts")
            return cur.fetchone()["cnt"]
    finally:
        conn.close()
