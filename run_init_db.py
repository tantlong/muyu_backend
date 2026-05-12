"""
执行 init_db.sql 初始化数据库
用法: python run_init_db.py
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3307)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "charset": "utf8mb4",
    "autocommit": True,
}

with open("init_db.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

conn = pymysql.connect(**config)
try:
    cursor = conn.cursor()
    # 逐条执行 SQL 语句
    statements = sql_content.split(";")
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            cursor.execute(stmt)
        except Exception as e:
            # 忽略 "database exists" 等错误
            if "already exists" in str(e) or "Duplicate" in str(e):
                print(f"[SKIP] {str(e)[:100]}")
            else:
                print(f"[ERROR] {str(e)[:200]}")
                print(f"  SQL: {stmt[:100]}...")
    print("数据库初始化完成!")
finally:
    cursor.close()
    conn.close()