from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import models, schemas, crud
from database import SessionLocal, engine
from utils import send_verify_code, verify_code, get_wechat_openid, check_commit_interval, check_commit_count

# 自动创建数据库表（首次启动执行，后续不重复创建）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="木鱼功德系统",
    description="本地开发版（适配微信测试号、短信模拟）",
    version="1.0.0"
)

# CORS跨域配置（允许小程序/UniApp前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态资源目录
app.mount("/static", StaticFiles(directory="static"), name="static")


# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------- 登录态校验与续期核心 --------------------------
def validate_and_renew_user(user: models.User, db: Session):
    """校验用户状态、登录态过期，并自动续期 last_active_at"""
    if not user:
        raise HTTPException(status_code=401, detail="登录态失效，请重新登录")
    # 强制失效：账号禁用(status=0)或锁定(status=2)
    if user.status != 1:
        status_msg = {0: "账号已被禁用，请联系客服", 2: "账号已被锁定，请联系客服"}.get(user.status, "账号状态异常")
        raise HTTPException(status_code=403, detail=status_msg)
    # 过期条件：连续 N 天无操作
    expire_days = int(os.getenv("TOKEN_EXPIRE_DAYS", 7))
    if user.last_active_at:
        now = datetime.utcnow()
        if now - user.last_active_at > timedelta(days=expire_days):
            raise HTTPException(status_code=401, detail="登录态过期，请重新登录")
    # 自动续期：更新最后活跃时间为当前时间
    user.last_active_at = datetime.utcnow()
    db.commit()
    return user


def validate_user_no_renew(user: models.User):
    """仅校验用户状态和登录态过期，但不续期 last_active_at（排行榜等只读接口使用）"""
    if not user:
        raise HTTPException(status_code=401, detail="登录态失效，请重新登录")
    if user.status != 1:
        status_msg = {0: "账号已被禁用，请联系客服", 2: "账号已被锁定，请联系客服"}.get(user.status, "账号状态异常")
        raise HTTPException(status_code=403, detail=status_msg)
    expire_days = int(os.getenv("TOKEN_EXPIRE_DAYS", 7))
    if user.last_active_at:
        now = datetime.utcnow()
        if now - user.last_active_at > timedelta(days=expire_days):
            raise HTTPException(status_code=401, detail="登录态过期，请重新登录")
    return True


# FastAPI 依赖：从查询参数获取 userSn，校验并续期（适用于 GET/POST query param 场景）
def get_current_user(
    userSn: str = Query(..., description="用户登录凭证（userSn）"),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_sn(db, userSn)
    return validate_and_renew_user(user, db)


# FastAPI 依赖：从请求体获取 userSn，校验并续期（适用于 POST body 场景）
def get_current_user_from_body(data: schemas.BaseUserSn, db: Session = Depends(get_db)):
    user = crud.get_user_by_sn(db, data.userSn)
    return validate_and_renew_user(user, db)


# FastAPI 依赖：从查询参数获取 userSn，仅校验不续期（排行榜等只读接口使用）
def get_current_user_no_renew(
    userSn: str = Query(..., description="用户登录凭证（userSn）"),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_sn(db, userSn)
    validate_user_no_renew(user)
    return user


# -------------------------- 短信验证码接口 --------------------------
@app.post("/api/send-code", summary="获取手机验证码")
def send_code(data: schemas.PhoneVerifyCode):
    if send_verify_code(data.phone):
        return {"code": 200, "msg": "验证码发送成功（本地模拟：123456）", "data": {"code": "123456"}}
    raise HTTPException(status_code=400, detail="验证码发送失败")


# -------------------------- 手机号登录/注册接口 --------------------------
@app.post("/api/app-login", summary="手机号登录/注册", response_model=schemas.LoginResponse)
def app_login(data: schemas.AppUserLogin, db: Session = Depends(get_db)):
    # 校验验证码
    if not verify_code(data.phone, data.code):
        raise HTTPException(status_code=400, detail="验证码错误")
    # 查询用户，未注册则创建
    user = crud.get_user_by_phone(db, data.phone)
    if not user:
        user = crud.create_user(db, phone=data.phone, nickname=f"用户{data.phone[-4:]}")
    # 登录即更新活跃时间（新用户 create_user 中已设置，此处对已有用户补充）
    user.last_active_at = datetime.utcnow()
    db.commit()
    # 获取用户等级
    level = crud.get_level_by_merit(db, user.merit_count)
    # 获取用户配置
    setting = crud.get_user_setting(db, user.id)
    return {
        "code": 200,
        "msg": "登录成功",
        "data": {
            "userSn": user.user_sn,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "phone": user.phone,
            "meritCount": user.merit_count,
            "levelName": level.level_name if level else "初心者",
            "levelColor": level.color if level else "#9E9E9E",
            "level": level.level if level else 1,
            "settings": {
                "fishSkin": setting.fish_skin if setting else "default",
                "hammerSkin": setting.hammer_skin if setting else "default",
                "knockSound": setting.knock_sound if setting else "default",
                "background": setting.background if setting else "default",
                "volume": setting.volume if setting else 80,
                "isVibrate": setting.is_vibrate if setting else 1,
                "autoFreq": setting.auto_freq if setting else 1000,
                "autoDuration": setting.auto_duration if setting else 0,
                "knockText": setting.knock_text if setting else "阿弥陀佛",
            }
        }
    }


# -------------------------- 微信登录接口 --------------------------
@app.post("/api/wechat-login", summary="微信登录", response_model=schemas.LoginResponse)
def wechat_login(data: schemas.WechatAuthCode, db: Session = Depends(get_db)):
    # 获取微信用户信息
    wechat_info = get_wechat_openid(data.code)
    if not wechat_info.get("openid"):
        raise HTTPException(status_code=400, detail="微信授权失败")
    # 查询用户，未注册则创建
    user = crud.get_user_by_openid(db, wechat_info["openid"])
    if not user:
        user = crud.create_user(
            db,
            openid=wechat_info["openid"],
            nickname=wechat_info.get("nickname", "微信用户"),
            avatar=wechat_info.get("avatar")
        )
    # 登录即更新活跃时间
    user.last_active_at = datetime.utcnow()
    db.commit()
    # 获取用户等级
    level = crud.get_level_by_merit(db, user.merit_count)
    # 获取用户配置
    setting = crud.get_user_setting(db, user.id)
    return {
        "code": 200,
        "msg": "微信登录成功",
        "data": {
            "userSn": user.user_sn,
            "openid": wechat_info["openid"],
            "nickname": user.nickname,
            "avatar": user.avatar,
            "meritCount": user.merit_count,
            "levelName": level.level_name if level else "初心者",
            "levelColor": level.color if level else "#9E9E9E",
            "level": level.level if level else 1,
            "settings": {
                "fishSkin": setting.fish_skin if setting else "default",
                "hammerSkin": setting.hammer_skin if setting else "default",
                "knockSound": setting.knock_sound if setting else "default",
                "background": setting.background if setting else "default",
                "volume": setting.volume if setting else 80,
                "isVibrate": setting.is_vibrate if setting else 1,
                "autoFreq": setting.auto_freq if setting else 1000,
                "autoDuration": setting.auto_duration if setting else 0,
                "knockText": setting.knock_text if setting else "阿弥陀佛",
            }
        }
    }


# -------------------------- 登录态校验接口 --------------------------
@app.get("/api/check-login-status", summary="检查登录态有效性（APP启动调用）")
def check_login_status(
    userSn: str = Query(..., description="用户登录凭证（userSn）"),
    db: Session = Depends(get_db)
):
    """APP启动时调用，校验userSn是否仍有效。有效则自动续期。"""
    user = crud.get_user_by_sn(db, userSn)
    if not user:
        return {"code": 401, "msg": "登录态失效", "data": {"isValid": False, "reason": "凭证不存在，请重新登录"}}
    if user.status != 1:
        status_msg = {0: "账号已被禁用", 2: "账号已被锁定"}.get(user.status, "账号状态异常")
        return {"code": 403, "msg": status_msg, "data": {"isValid": False, "reason": status_msg}}
    expire_days = int(os.getenv("TOKEN_EXPIRE_DAYS", 7))
    if user.last_active_at:
        now = datetime.utcnow()
        if now - user.last_active_at > timedelta(days=expire_days):
            return {"code": 401, "msg": "登录态过期", "data": {"isValid": False, "reason": f"连续{expire_days}天未活跃，请重新登录"}}
    # 有效则自动续期
    user.last_active_at = datetime.utcnow()
    db.commit()
    return {"code": 200, "msg": "登录态有效", "data": {"isValid": True}}


# -------------------------- 微信号捆绑接口 --------------------------
@app.post("/api/wechat-bind", summary="微信号捆绑已有账号")
def wechat_bind(
    data: schemas.WechatBindRequest,
    db: Session = Depends(get_db)
):
    # 使用 body 中的 userSn 进行登录态校验与续期
    user = crud.get_user_by_sn(db, data.userSn)
    validate_and_renew_user(user, db)
    # 获取微信openid
    wechat_info = get_wechat_openid(data.code)
    if not wechat_info.get("openid"):
        raise HTTPException(status_code=400, detail="微信授权失败")
    # 执行捆绑
    if crud.bind_wechat(db, data.userSn, wechat_info["openid"]):
        return {"code": 200, "msg": "捆绑成功"}
    raise HTTPException(status_code=400, detail="捆绑失败，该微信号已被捆绑")


# -------------------------- 功德提交接口 --------------------------
@app.post("/api/knock-submit", summary="功德敲击提交")
def knock_submit(
    data: schemas.KnockSubmit,
    db: Session = Depends(get_db)
):
    # 使用 body 中的 userSn 进行登录态校验与续期
    user = crud.get_user_by_sn(db, data.userSn)
    validate_and_renew_user(user, db)
    # 校验提交间隔和次数
    if not check_commit_interval(data.userSn, data.isAuto):
        raise HTTPException(status_code=403, detail="提交过于频繁，请稍后再试")
    valid_count = check_commit_count(data.count, data.isAuto)
    # 增加功德
    user = crud.add_merit(db, user, valid_count)
    # 获取等级
    level = crud.get_level_by_merit(db, user.merit_count)
    return {
        "code": 200,
        "msg": "功德提交成功",
        "data": {
            "meritCount": user.merit_count,
            "addedCount": valid_count,
            "levelName": level.level_name if level else "初心者",
            "levelColor": level.color if level else "#9E9E9E",
            "level": level.level if level else 1,
        }
    }


# -------------------------- 用户信息接口 --------------------------
@app.get("/api/user-info", summary="获取用户信息")
def get_user_info(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户信息，自动校验登录态并续期"""
    level = crud.get_level_by_merit(db, user.merit_count)
    setting = crud.get_user_setting(db, user.id)
    return {
        "code": 200,
        "msg": "获取成功",
        "data": {
            "userSn": user.user_sn,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "phone": user.phone,
            "meritCount": user.merit_count,
            "province": user.province,
            "levelName": level.level_name if level else "初心者",
            "levelColor": level.color if level else "#9E9E9E",
            "level": level.level if level else 1,
            "settings": {
                "fishSkin": setting.fish_skin if setting else "default",
                "hammerSkin": setting.hammer_skin if setting else "default",
                "knockSound": setting.knock_sound if setting else "default",
                "background": setting.background if setting else "default",
                "volume": setting.volume if setting else 80,
                "isVibrate": setting.is_vibrate if setting else 1,
                "autoFreq": setting.auto_freq if setting else 1000,
                "autoDuration": setting.auto_duration if setting else 0,
                "knockText": setting.knock_text if setting else "阿弥陀佛",
            }
        }
    }


# -------------------------- 个性化配置保存接口 --------------------------
@app.post("/api/save-settings", summary="保存个性化配置")
def save_settings(
    data: schemas.UserSettingSave = None,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存个性化配置，自动校验登录态并续期"""
    kwargs = {}
    if data:
        kwargs = data.model_dump(exclude_none=True)
    setting = crud.save_user_setting(db, user.id, **kwargs)
    return {
        "code": 200,
        "msg": "保存成功",
        "data": {
            "fishSkin": setting.fish_skin,
            "hammerSkin": setting.hammer_skin,
            "knockSound": setting.knock_sound,
            "background": setting.background,
            "volume": setting.volume,
            "isVibrate": setting.is_vibrate,
            "autoFreq": setting.auto_freq,
            "autoDuration": setting.auto_duration,
            "knockText": setting.knock_text,
        }
    }


# -------------------------- 排行榜模块接口 --------------------------

@app.get("/api/rank/person", summary="个人排行榜（按功德降序）")
def rank_person(
    limit: int = Query(100, description="返回数量"),
    user: models.User = Depends(get_current_user_no_renew),
    db: Session = Depends(get_db)
):
    """返回个人排行榜：rank、avatar、nickname、meritCount、province，只返回正常用户"""
    users = crud.get_person_ranking(db, limit)
    ranking_list = []
    for rank, u in enumerate(users, 1):
        ranking_list.append({
            "rank": rank,
            "avatar": u.avatar,
            "nickname": u.nickname,
            "meritCount": u.merit_count,
            "province": u.province,
        })
    return {
        "code": 200,
        "msg": "获取成功",
        "data": {"list": ranking_list}
    }


@app.get("/api/rank/province", summary="省份排行榜（按省份总功德降序）")
def rank_province(
    user: models.User = Depends(get_current_user_no_renew),
    db: Session = Depends(get_db)
):
    """返回：rank、province、meritCount，按省份总功德降序"""
    results = crud.get_province_ranking_aggregated(db)
    province_list = []
    for rank, row in enumerate(results, 1):
        province_list.append({
            "rank": rank,
            "province": row.province,
            "meritCount": row.total_merit,
        })
    return {
        "code": 200,
        "msg": "获取成功",
        "data": {"list": province_list}
    }


@app.get("/api/rank/my", summary="我的排名")
def rank_my(
    user: models.User = Depends(get_current_user_no_renew),
    db: Session = Depends(get_db)
):
    """返回：myRank、myProvinceRank、meritCount、province"""
    my_rank = crud.get_user_nationwide_rank(db, user.merit_count)
    my_province_rank = crud.get_user_province_rank(db, user.province, user.merit_count)
    return {
        "code": 200,
        "msg": "获取成功",
        "data": {
            "myRank": my_rank,
            "myProvinceRank": my_province_rank,
            "meritCount": user.merit_count,
            "province": user.province,
        }
    }


@app.get("/api/rank/total-merit", summary="全平台总功德")
def rank_total_merit(
    user: models.User = Depends(get_current_user_no_renew),
    db: Session = Depends(get_db)
):
    """返回：totalMerit"""
    total = crud.get_total_merit(db)
    return {
        "code": 200,
        "msg": "获取成功",
        "data": {"totalMerit": total}
    }


# -------------------------- 功德等级列表接口 --------------------------
@app.get("/api/levels", summary="获取所有等级配置")
def get_levels(db: Session = Depends(get_db)):
    """等级列表为公开接口，不校验登录态"""
    levels = db.query(models.UserLevel).filter(models.UserLevel.status == 1).order_by(models.UserLevel.level).all()
    level_list = []
    for lv in levels:
        level_list.append({
            "level": lv.level,
            "levelName": lv.level_name,
            "minMerit": lv.min_merit,
            "maxMerit": lv.max_merit,
            "color": lv.color,
        })
    return {
        "code": 200,
        "msg": "获取成功",
        "data": {"levels": level_list}
    }


# -------------------------- 更新用户昵称接口 --------------------------
@app.post("/api/update-nickname", summary="更新用户昵称")
def update_nickname(
    nickname: str = Query(..., description="新昵称"),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户昵称，自动校验登录态并续期"""
    if not nickname or len(nickname) > 50:
        raise HTTPException(status_code=400, detail="昵称长度需在1-50字符之间")
    user.nickname = nickname
    db.commit()
    return {"code": 200, "msg": "更新成功", "data": {"nickname": nickname}}


# -------------------------- 更新省份接口 --------------------------
@app.post("/api/update-province", summary="更新用户所在省份")
def update_province(
    province: str = Query(..., description="省份名称"),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户所在省份，自动校验登录态并续期"""
    user.province = province
    db.commit()
    return {"code": 200, "msg": "更新成功", "data": {"province": province}}


# -------------------------- 启动入口 --------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)