
"""
检查并修复 users 表字段注释乱码问题
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

# 正确的字段注释
correct_fields = [
    ("id", "BIGINT", "内部自增主键，仅后端使用"),
    ("user_sn", "VARCHAR(32) NOT NULL", "用户对外唯一编码（U+15位字母数字）"),
    ("openid", "VARCHAR(100) NULL", "微信openid（微信登录/捆绑用，未捆绑则为空）"),
    ("nickname", "VARCHAR(50) NULL", "用户昵称"),
    ("avatar", "VARCHAR(255) NULL", "用户头像地址（本地用static目录，上线用OSS）"),
    ("phone", "VARCHAR(20) NULL", "手机号（手机号登录用，未注册则为空）"),
    ("merit_count", "BIGINT DEFAULT 0", "累计功德数（核心字段）"),
    ("province", "VARCHAR(50) NULL", "所在省份（用于省份排行榜）"),
    ("status", "TINYINT DEFAULT 1", "账号状态：1正常，0禁用"),
    ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP", "创建时间"),
    ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "更新时间")
]

conn = pymysql.connect(**config)
try:
    cursor = conn.cursor()
    
    # 查看当前表结构
    print("=== 当前 users 表字段注释 ===")
    cursor.execute("SHOW FULL COLUMNS FROM users")
    columns = cursor.fetchall()
    for col in columns:
        name = col[0]
        comment = col[8]
        print(f"  {name}: {comment}")
    
    # 询问是否修复
    print("\n是否修复字段注释? (y/n)")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\n=== 开始修复 ===")
        for field_name, field_type, comment in correct_fields:
            sql = f"ALTER TABLE users MODIFY COLUMN {field_name} {field_type} COMMENT '{comment}'"
            try:
                cursor.execute(sql)
                print(f"  ✓ {field_name} 已修复")
            except Exception as e:
                print(f"  ✗ {field_name} 修复失败: {e}")
        
        # 更新表注释
        cursor.execute("ALTER TABLE users COMMENT = '用户基础表'")
        print("  ✓ 表注释已修复")
        
        print("\n=== 修复完成 ===")
        
        # 再次查看
        print("\n=== 修复后的 users 表字段注释 ===")
        cursor.execute("SHOW FULL COLUMNS FROM users")
        columns = cursor.fetchall()
        for col in columns:
            name = col[0]
            comment = col[8]
            print(f"  {name}: {comment}")
            
finally:
    cursor.close()
    conn.close()

