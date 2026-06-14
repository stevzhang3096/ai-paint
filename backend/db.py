"""数据库 — MySQL 版（pymysql）"""
import hashlib
import os
import pymysql
from pymysql.cursors import DictCursor
from config import MYSQL_CONFIG

def init_processed_tx_table():
    """初始化 processed_tx 表"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS processed_tx (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    txid VARCHAR(255) UNIQUE NOT NULL,
                    user_id INT NOT NULL,
                    usdt_amount DECIMAL(10,2) NOT NULL,
                    credits INT NOT NULL,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
    finally:
        conn.close()

def is_tx_processed(txid):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM processed_tx WHERE txid=%s", (txid,))
            return cur.fetchone() is not None
    finally:
        conn.close()

def save_processed_tx(txid, user_id, usdt_amount, credits):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT IGNORE INTO processed_tx (txid, user_id, usdt_amount, credits) VALUES (%s, %s, %s, %s)",
                (txid, user_id, usdt_amount, credits)
            )
        conn.commit()
    finally:
        conn.close()

def get_conn():
    return pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset=MYSQL_CONFIG["charset"],
        cursorclass=DictCursor
    )

def init_db():
    """表已通过建表脚本创建，本函数仅做保留兼容"""
    conn = get_conn()
    conn.close()
    return True

# ── 用户 ──

def create_user(email, password):
    conn = get_conn()
    try:
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password, credits) VALUES (%s, %s, %s)",
                (email, pw_hash, 0)
            )
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
        return user
    except pymysql.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
        return user
    finally:
        conn.close()

def verify_login(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    return user if user["password"] == pw_hash else None

def get_user(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, credits, role, password FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
        return user
    finally:
        conn.close()

def add_credits(user_id, amount):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET credits = credits + %s WHERE id=%s", (amount, user_id))
        conn.commit()
    finally:
        conn.close()

def deduct_credit(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET credits = credits - 1 WHERE id=%s AND credits > 0", (user_id,))
        conn.commit()
    finally:
        conn.close()

def get_user_credits(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT credits FROM users WHERE id=%s", (user_id,))
            row = cur.fetchone()
        return row["credits"] if row else 0
    finally:
        conn.close()

def update_password(email, pw_hash):
    """更新用户密码（找回密码用）"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET password=%s WHERE email=%s", (pw_hash, email))
        conn.commit()
    finally:
        conn.close()

# ── 生成记录 ──

def save_generation(user_id, prompt, model, size, image_url, local_file=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO generations (user_id, prompt, model, size, image_url, local_file) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, prompt, model, size, image_url, local_file)
            )
            gen_id = cur.lastrowid
        conn.commit()
        return gen_id
    finally:
        conn.close()

def get_generation(gen_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM generations WHERE id=%s", (gen_id,))
            row = cur.fetchone()
        return row
    finally:
        conn.close()

def delete_generation(gen_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM generations WHERE id=%s", (gen_id,))
        conn.commit()
    finally:
        conn.close()

def get_user_generations(user_id, limit=20):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM generations WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
                (user_id, limit)
            )
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()

# ── 订单 ──

def get_user_orders(user_id, limit=20):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM orders WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
                (user_id, limit)
            )
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()

# ── 套餐 ──

def get_plans(active_only=True):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if active_only:
                cur.execute("SELECT * FROM plans WHERE is_active=1 ORDER BY sort_order")
            else:
                cur.execute("SELECT * FROM plans ORDER BY sort_order")
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()

def get_plan_by_name(name):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM plans WHERE name=%s", (name,))
            row = cur.fetchone()
        return row
    finally:
        conn.close()

def get_admin_stats():
    """后台首页统计数据"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM users")
            total_users = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) as cnt FROM generations")
            total_generations = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role=1")
            total_admins = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE status='confirmed'")
            total_orders = cur.fetchone()['cnt']
            cur.execute("SELECT COALESCE(SUM(usdt_amount), 0) as total FROM orders WHERE status='confirmed'")
            total_revenue = cur.fetchone()['total']
            cur.execute("SELECT COALESCE(SUM(credits), 0) as total FROM users")
            total_credits = cur.fetchone()['total']
            # 今日注册
            cur.execute("SELECT COUNT(*) as cnt FROM users WHERE DATE(created_at) = CURDATE()")
            today_users = cur.fetchone()['cnt']
            # 今日生成
            cur.execute("SELECT COUNT(*) as cnt FROM generations WHERE DATE(created_at) = CURDATE()")
            today_gens = cur.fetchone()['cnt']
            # 套餐数
            cur.execute("SELECT COUNT(*) as cnt FROM plans WHERE is_active=1")
            active_plans = cur.fetchone()['cnt']
        return {
            "total_users": total_users,
            "total_generations": total_generations,
            "total_admins": total_admins,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "total_credits": total_credits,
            "today_users": today_users,
            "today_generations": today_gens,
            "active_plans": active_plans,
        }
    finally:
        conn.close()

def create_order(user_id, txid, usdt_amount, plan_name, credits):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (user_id, txid, usdt_amount, plan_name, credits) VALUES (%s, %s, %s, %s, %s)",
                (user_id, txid, usdt_amount, plan_name, credits)
            )
        conn.commit()
    finally:
        conn.close()

def confirm_order(txid):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE txid=%s", (txid,))
            order = cur.fetchone()
            if order and order["status"] == "pending":
                cur.execute("UPDATE orders SET status='confirmed' WHERE txid=%s", (txid,))
                cur.execute("UPDATE users SET credits = credits + %s WHERE id=%s", (order["credits"], order["user_id"]))
                conn.commit()
        return order
    finally:
        conn.close()
