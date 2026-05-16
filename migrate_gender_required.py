"""
修改 users 表的 gender 字段：改为必填，默认值为0
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
    
    # 首先将 NULL 值更新为 0
    cursor.execute("UPDATE users SET gender = 0 WHERE gender IS NULL")
    print(f"已将 {cursor.rowcount} 条 NULL 值更新为 0")
    
    # 修改字段为 NOT NULL 并设置默认值为 0
    cursor.execute("ALTER TABLE users MODIFY COLUMN gender TINYINT NOT NULL DEFAULT 0 COMMENT '性别：0未知，1男，2女'")
    print("已将 gender 字段改为必填，默认值为 0")
    
    # 验证修改结果
    print("\n验证 users 表 gender 字段...")
    cursor.execute("""
        SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'gender'
    """, (os.getenv("DB_NAME", "muyu_db"),))
    
    result = cursor.fetchone()
    print(f"  字段名: {result[0]}")
    print(f"  是否可空: {result[1]}")
    print(f"  默认值: {result[2]}")
    
    print("\n修改完成！")
        
finally:
    cursor.close()
    conn.close()

