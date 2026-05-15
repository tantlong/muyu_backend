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

    # 无昵称时自动生成佛系随机昵称 超大词库 6400组合
    if not nickname:
        adj_list = [
            # 禅意佛系
            "静心", "清宁", "悠然", "淡然", "安和", "温婉", "清雅", "无尘", "空灵", "平和",
            "温柔", "静谧", "浅念", "归尘", "栖云", "听风", "观月", "知意", "忘忧", "随缘",
            "清风", "明月", "星落", "云舒", "山涧", "林间", "暮晚", "朝晨", "素心", "安然",
            "慈悲", "欢喜", "静守", "闲庭", "浮生", "流年", "浅安", "清欢", "孤屿", "寒舟",
            "青岚", "白霜", "暮雪", "初晴", "听雨", "寻幽", "揽星", "枕月", "沐风", "怀瑾",
            "疏影", "微凉", "静默", "如初", "浅笑", "离尘", "绝尘", "清寂", "幽然", "宁安",
            "静好", "空寂", "恬淡", "清远", "素净", "澄心", "一念", "三生", "半盏", "千寻",
            "阡陌", "未央", "灵秀", "娴静", "澹然", "虚怀",

            # 简约文艺（新增扩充）
            "晚风", "山野", "朝暮", "人间", "星河", "初见", "偏爱", "拾光", "屿风", "南枝",
            "浅夏", "晚秋", "温茶", "白茶", "清昼", "长夜", "朝夕", "赴野", "留白", "半度",
            "知夏", "知秋", "赴安", "望舒", "南屿", "北笙", "江月", "川行", "云栖", "雾隐",
            "青梧", "半夏", "凉生", "安夏", "流年", "时柒", "枕星", "栖鹤", "书尽", "辞晚",

            # 可爱温柔（新增扩充）
            "软软", "甜甜", "萌萌", "奶味", "暖心", "小橘", "小鹿", "星星", "云朵", "桃桃",
            "芋圆", "糯米", "乖乖", "泡泡", "绵绵", "糖糖", "栗子", "橘夏",
            "奶酥", "奶芙", "甜糯", "温软", "小甜", "小软", "晴晴", "安安", "朵朵", "兮兮",
            "柠萌", "栀夏", "莓果", "软糖", "甜柚", "浅莓", "初甜", "圆子", "团子", "啵啵"
        ]

        noun_list = [
            # 禅意佛系
            "木鱼", "菩提", "莲花", "禅心", "功德", "行者", "居士", "心灯", "灯盏", "星辰",
            "云朵", "山海", "松鹤", "竹影", "山泉", "古寺", "清潭", "月影", "晚风", "归人",
            "书生", "仙人", "闲客", "过客", "青衫", "白衣", "空山", "幽谷", "晨钟", "暮鼓",
            "茶烟", "墨香", "琴音", "诗行", "清梦", "人间", "凡尘", "灵犀", "素笺", "远山",
            "近川", "寒松", "幽兰", "静竹", "闲梅", "轻舟", "孤鸿", "寒鸦", "秋霜", "暮烟",
            "朝露", "清溪", "云崖", "松涛", "竹径", "苔痕", "梵音", "经卷", "禅院", "山寺",
            "星河", "碧落", "红尘", "天涯", "海角", "孤山", "长亭", "短巷", "古巷", "疏桐",
            "残荷", "晚舟", "寒江", "青山", "长川", "风月",

            # 简约文艺（新增扩充）
            "落日", "森林", "海岛", "街角", "晴空", "雾里", "林间", "山野", "朝暮", "光年",
            "小城", "时光", "江川", "归舟", "长街", "旧巷", "烟雨", "南风", "北港", "西洲",
            "青川", "雾山", "云城", "星野", "空巷", "凉城", "南河", "北渡", "山止", "川眠",

            # 可爱治愈（新增扩充）
            "小兔", "猫咪", "团子", "月亮", "汽水", "奶茶", "糖果", "小熊", "泡芙", "蛋挞",
            "草莓", "蜜桃", "银河", "小鹿", "松果", "糯米",
            "奶猫", "软兔", "甜熊", "柠柠", "栀栀", "莓莓", "糖丸", "奶团", "圆子", "啵啵",
            "风铃", "纸鸢", "甜品", "星袋", "月窝", "云屋", "橘猫", "仓鼠", "肥兔", "甜鹿"
        ]

        import random
        nickname = f"{random.choice(adj_list)}的{random.choice(noun_list)}"

    # 构建用户对象
    user = models.User(
        user_sn=user_sn,
        openid=openid,
        phone=phone,
        nickname=nickname,
        avatar=avatar or "/static/default_avatar.png?v=1",
        merit_count=0,
        province=province,
        status=1,
        last_active_at=datetime.utcnow()
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
        'isShowBase': 'is_show_base',  # 是否显示木鱼底座
        'baseSkin': 'base_skin',  # 木鱼底座皮肤标识
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
