"""
检查用户表中头像URL的实际格式
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
    "database": os.getenv("DB_NAME", "muyu_db"),
    "charset": "utf8mb4",
    "autocommit": True,
}

conn = pymysql.connect(**config)
try:
    cursor = conn.cursor()
    
    # 查询所有用户的头像URL
    cursor.execute("SELECT id, nickname, avatar FROM users LIMIT 15")
    print("当前数据库中的头像URL：")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}: {repr(row[2])}")
        
finally:
    cursor.close()
    conn.close()

