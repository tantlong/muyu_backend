"""
批量更新用户表中旧的默认头像URL为相对路径
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
    
    # 查询有多少用户使用了旧的默认头像URL
    cursor.execute("SELECT COUNT(*) FROM users WHERE avatar LIKE 'http://localhost%'")
    count = cursor.fetchone()[0]
    print(f"发现 {count} 条记录使用了旧的URL格式")
    
    if count > 0:
        # 更新为相对路径（处理包含端口号的情况）
        cursor.execute("UPDATE users SET avatar = REPLACE(avatar, 'http://localhost:8000/static/', '/static/') WHERE avatar LIKE 'http://localhost:8000%'")
        cursor.execute("UPDATE users SET avatar = REPLACE(avatar, 'http://localhost/static/', '/static/') WHERE avatar LIKE 'http://localhost%'")
        print(f"已更新 {cursor.rowcount} 条记录")
        
        # 验证更新结果
        cursor.execute("SELECT COUNT(*) FROM users WHERE avatar LIKE 'http://localhost%'")
        remaining = cursor.fetchone()[0]
        print(f"更新后剩余 {remaining} 条记录使用旧URL格式")
        
        # 显示一些示例记录
        cursor.execute("SELECT id, nickname, avatar FROM users WHERE avatar LIKE '/static/%' LIMIT 5")
        print("\n更新后的头像URL示例：")
        for row in cursor.fetchall():
            print(f"  {row[1]}: {row[2]}")
    else:
        print("没有需要更新的记录")
        
finally:
    cursor.close()
    conn.close()

