
"""
修复 created_at 和 updated_at 字段的注释
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
    
    print("=== 修复剩余字段注释 ===")
    
    # 修复 created_at
    sql1 = "ALTER TABLE users MODIFY COLUMN `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'"
    try:
        cursor.execute(sql1)
        print("  created_at 已修复")
    except Exception as e:
        print(f"  created_at 修复失败: {e}")
    
    # 修复 updated_at
    sql2 = "ALTER TABLE users MODIFY COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"
    try:
        cursor.execute(sql2)
        print("  updated_at 已修复")
    except Exception as e:
        print(f"  updated_at 修复失败: {e}")
    
    # 查看最终结果
    print("\n=== 最终 users 表字段注释 ===")
    cursor.execute("SHOW FULL COLUMNS FROM users")
    columns = cursor.fetchall()
    for col in columns:
        name = col[0]
        comment = col[8]
        print(f"  {name}: {comment}")
        
finally:
    cursor.close()
    conn.close()

