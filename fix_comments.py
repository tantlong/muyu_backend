
"""
自动修复 users 表字段注释乱码问题
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

# 正确的字段注释，只修改注释
correct_comments = {
    "id": "内部自增主键，仅后端使用",
    "user_sn": "用户对外唯一编码（U+15位字母数字）",
    "openid": "微信openid（微信登录/捆绑用，未捆绑则为空）",
    "nickname": "用户昵称",
    "avatar": "用户头像地址（本地用static目录，上线用OSS）",
    "phone": "手机号（手机号登录用，未注册则为空）",
    "merit_count": "累计功德数（核心字段）",
    "province": "所在省份（用于省份排行榜）",
    "status": "账号状态：1正常，0禁用",
    "created_at": "创建时间",
    "updated_at": "更新时间"
}

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
    
    print("\n=== 开始修复 ===")
    
    # 获取当前表的完整定义
    cursor.execute("SHOW CREATE TABLE users")
    create_sql = cursor.fetchone()[1]
    
    # 使用信息架构获取字段定义
    cursor.execute("""
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLUMN_KEY
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users'
        ORDER BY ORDINAL_POSITION
    """, (os.getenv("DB_NAME", "muyu_db"),))
    
    cols = cursor.fetchall()
    
    for col in cols:
        col_name, col_type, is_nullable, col_default, extra, col_key = col
        
        # 构建字段定义
        def_parts = [col_type]
        
        if is_nullable == "NO":
            def_parts.append("NOT NULL")
        else:
            def_parts.append("NULL")
        
        if col_default is not None:
            if col_default.upper() == "CURRENT_TIMESTAMP":
                def_parts.append(f"DEFAULT {col_default}")
            else:
                def_parts.append(f"DEFAULT '{col_default}'")
        
        if extra:
            def_parts.append(extra)
        
        field_def = " ".join(def_parts)
        
        # 获取正确注释
        new_comment = correct_comments.get(col_name, "")
        
        # 执行修改
        sql = f"ALTER TABLE users MODIFY COLUMN `{col_name}` {field_def} COMMENT %s"
        try:
            cursor.execute(sql, (new_comment,))
            print(f"  {col_name} 已修复")
        except Exception as e:
            print(f"  {col_name} 修复失败: {e}")
    
    # 更新表注释
    cursor.execute("ALTER TABLE users COMMENT = '用户基础表'")
    print("  表注释已修复")
    
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

