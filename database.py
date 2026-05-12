from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 加载环境变量（指定UTF-8编码，避免解码错误）
load_dotenv(encoding="utf-8")

# 数据库连接地址（从.env获取，避免硬编码，适配本地/服务器切换）
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}?charset=utf8mb4"
)

# 创建数据库引擎（自带连接池，本地开发默认配置足够，无需修改）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True  # 连接前校验，避免无效连接
)

# 创建会话工厂（每次请求创建一个会话，用完关闭，线程安全）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础ORM模型（所有模型继承此类）
Base = declarative_base()