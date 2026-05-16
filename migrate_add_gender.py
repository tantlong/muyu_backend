"""
向 users 表添加 gender 字段（性别：0未知，1男，2女，可空）
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
    
    # 检查 gender 字段是否已存在
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'gender'
    """, (os.getenv("DB_NAME", "muyu_db"),))
    
    if cursor.fetchone()[0] == 0:
        print("正在添加 gender 字段...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN gender TINYINT NULL COMMENT '性别：0未知，1男，2女'
            AFTER phone
        """)
        print("gender 字段添加成功")
    else:
        print("gender 字段已存在，跳过添加")
    
    # 验证添加结果
    print("\n验证 users 表结构...")
    cursor.execute("SHOW FULL COLUMNS FROM users")
    columns = cursor.fetchall()
    print("\nusers 表字段列表（部分）：")
    for col in columns[:20]:
        name = col[0]
        comment = col[8]
        print(f"  {name}: {comment}")
        
    print("\n迁移完成！")
        
finally:
    cursor.close()
    conn.close()

