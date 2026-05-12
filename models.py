from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, func
from database import Base


# 用户基础表（适配微信登录、手机号登录，本地开发友好）
class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    user_sn = Column(String(32), unique=True, index=True, nullable=False)
    openid = Column(String(100), unique=True, index=True)  # 微信openid，可为空
    nickname = Column(String(50))
    avatar = Column(String(255))  # 本地：static目录地址，上线：OSS地址
    phone = Column(String(20), unique=True, index=True)  # 手机号，可为空
    merit_count = Column(BigInteger, default=0)
    province = Column(String(50))
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# 用户个性化配置表（新用户自动初始化）
class UserSetting(Base):
    __tablename__ = "user_settings"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    fish_skin = Column(String(50), default="default")
    hammer_skin = Column(String(50), default="default")
    knock_sound = Column(String(50), default="default")
    background = Column(String(50), default="default")
    volume = Column(Integer, default=80)
    is_vibrate = Column(SmallInteger, default=1)
    auto_freq = Column(Integer, default=1000)
    auto_duration = Column(Integer, default=0)
    knock_text = Column(String(100), default="阿弥陀佛")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# 用户等级表（与初始数据对应）
class UserLevel(Base):
    __tablename__ = "user_levels"
    id = Column(Integer, primary_key=True)
    level = Column(Integer, unique=True)
    level_name = Column(String(50))
    min_merit = Column(BigInteger)
    max_merit = Column(BigInteger)
    color = Column(String(50), default="#ffffff")
    status = Column(SmallInteger, default=1)
