"""
向 user_settings 表添加新字段：is_show_base 和 base_skin
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
    
    # 检查 is_show_base 字段是否已存在
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'user_settings' 
        AND COLUMN_NAME = 'is_show_base'
    """, (os.getenv("DB_NAME", "muyu_db"),))
    
    if cursor.fetchone()[0] == 0:
        print("正在添加 is_show_base 字段...")
        cursor.execute("""
            ALTER TABLE user_settings 
            ADD COLUMN is_show_base TINYINT DEFAULT 1 COMMENT '是否显示木鱼底座：1开启，0关闭'
            AFTER knock_text
        """)
        print("is_show_base 字段添加成功")
    else:
        print("is_show_base 字段已存在，跳过添加")
    
    # 检查 base_skin 字段是否已存在
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'user_settings' 
        AND COLUMN_NAME = 'base_skin'
    """, (os.getenv("DB_NAME", "muyu_db"),))
    
    if cursor.fetchone()[0] == 0:
        print("正在添加 base_skin 字段...")
        cursor.execute("""
            ALTER TABLE user_settings 
            ADD COLUMN base_skin VARCHAR(50) DEFAULT 'default' COMMENT '木鱼底座皮肤标识'
            AFTER is_show_base
        """)
        print("base_skin 字段添加成功")
    else:
        print("base_skin 字段已存在，跳过添加")
    
    # 验证添加结果
    print("\n验证 user_settings 表结构...")
    cursor.execute("SHOW FULL COLUMNS FROM user_settings")
    columns = cursor.fetchall()
    print("\nuser_settings 表字段列表：")
    for col in columns:
        name = col[0]
        comment = col[8]
        print(f"  {name}: {comment}")
        
    print("\n迁移完成！")
        
finally:
    cursor.close()
    conn.close()
