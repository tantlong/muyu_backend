from sqlalchemy.orm import Session
from datetime import datetime
import models
from utils import generate_user_sn


# 根据userSn查询用户（token校验核心）
def get_user_by_sn(db: Session, user_sn: str):
    return db.query(models.User).filter(models.User.user_sn == user_sn).first()


# 根据手机号查询用户（手机号登录用）
def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


# 根据openid查询用户（微信登录/捆绑用）
def get_user_by_openid(db: Session, openid: str):
    return db.query(models.User).filter(models.User.openid == openid).first()


# 创建用户（微信、手机号注册通用，自动初始化配置）
def create_user(db: Session, openid=None, phone=None, nickname=None, avatar=None, province=None):
    # 生成唯一userSn（重复则重新生成）
    while True:
        user_sn = generate_user_sn()
        if not get_user_by_sn(db, user_sn):
            break
    # 构建用户对象
    user = models.User(
        user_sn=user_sn,
        openid=openid,
        phone=phone,
        nickname=nickname or (f"用户{phone[-4:]}" if phone else "木鱼用户"),
        avatar=avatar or "http://localhost:8000/static/default_avatar.png",
        merit_count=0,
        province=province,
        status=1,
        last_active_at=datetime.utcnow()  # 注册即视为首次活跃
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # 自动初始化个性化配置
    setting = models.UserSetting(user_id=user.id)
    db.add(setting)
    db.commit()
    return user


# 微信号捆绑（关联已有用户和openid）
def bind_wechat(db: Session, user_sn: str, openid: str) -> bool:
    user = get_user_by_sn(db, user_sn)
    if not user or get_user_by_openid(db, openid):
        return False
    user.openid = openid
    db.commit()
    db.refresh(user)
    return True


# 增加功德（核心操作）
def add_merit(db: Session, user, count: int):
    user.merit_count += count
    db.commit()
    db.refresh(user)
    return user


# 根据功德数获取等级（自动匹配）
def get_level_by_merit(db: Session, merit: int):
    return db.query(models.UserLevel).filter(
        models.UserLevel.min_merit <= merit,
        models.UserLevel.max_merit >= merit,
        models.UserLevel.status == 1
    ).first()


# 获取用户配置
def get_user_setting(db: Session, user_id: int):
    return db.query(models.UserSetting).filter(models.UserSetting.user_id == user_id).first()


# 保存/更新用户配置
def save_user_setting(db: Session, user_id: int, **kwargs):
    setting = get_user_setting(db, user_id)
    if not setting:
        setting = models.UserSetting(user_id=user_id)
        db.add(setting)
    # 字段映射：驼峰 -> 下划线
    field_map = {
        'fishSkin': 'fish_skin',
        'hammerSkin': 'hammer_skin',
        'knockSound': 'knock_sound',
        'background': 'background',
        'volume': 'volume',
        'isVibrate': 'is_vibrate',
        'autoFreq': 'auto_freq',
        'autoDuration': 'auto_duration',
        'knockText': 'knock_text',
    }
    for camel_key, value in kwargs.items():
        if value is not None and camel_key in field_map:
            setattr(setting, field_map[camel_key], value)
    db.commit()
    db.refresh(setting)
    return setting


# 获取省份排行榜（按功德数降序）
def get_province_ranking(db: Session, province: str, limit: int = 100):
    return db.query(models.User).filter(
        models.User.province == province,
        models.User.status == 1
    ).order_by(models.User.merit_count.desc()).limit(limit).all()


# 获取全国排行榜（按功德数降序）
def get_nationwide_ranking(db: Session, limit: int = 100):
    return db.query(models.User).filter(
        models.User.status == 1
    ).order_by(models.User.merit_count.desc()).limit(limit).all()


# 获取个人排行榜（按功德数降序，只返回正常用户）
def get_person_ranking(db: Session, limit: int = 100):
    return db.query(models.User).filter(
        models.User.status == 1
    ).order_by(models.User.merit_count.desc()).limit(limit).all()


# 获取省份排行榜（按省份总功德降序，聚合查询）
def get_province_ranking_aggregated(db: Session):
    from sqlalchemy import func as sa_func
    results = db.query(
        models.User.province,
        sa_func.sum(models.User.merit_count).label('total_merit')
    ).filter(
        models.User.status == 1,
        models.User.province.isnot(None),
        models.User.province != ''
    ).group_by(models.User.province).order_by(
        sa_func.sum(models.User.merit_count).desc()
    ).all()
    return results


# 获取用户在全国的排名
def get_user_nationwide_rank(db: Session, merit_count: int) -> int:
    count = db.query(models.User).filter(
        models.User.status == 1,
        models.User.merit_count > merit_count
    ).count()
    return count + 1


# 获取用户在所在省份的排名
def get_user_province_rank(db: Session, province: str, merit_count: int) -> int:
    if not province:
        return 0
    count = db.query(models.User).filter(
        models.User.status == 1,
        models.User.province == province,
        models.User.merit_count > merit_count
    ).count()
    return count + 1


# 获取全平台总功德
def get_total_merit(db: Session) -> int:
    from sqlalchemy import func as sa_func
    result = db.query(sa_func.coalesce(sa_func.sum(models.User.merit_count), 0)).filter(
        models.User.status == 1
    ).scalar()
    return result
