from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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


# -------------------------- 微信号捆绑接口 --------------------------
@app.post("/api/wechat-bind", summary="微信号捆绑已有账号")
def wechat_bind(data: schemas.WechatBindRequest, db: Session = Depends(get_db)):
    # 查询用户是否存在
    user = crud.get_user_by_sn(db, data.userSn)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
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
def knock_submit(data: schemas.KnockSubmit, db: Session = Depends(get_db)):
    # 查询用户
    user = crud.get_user_by_sn(db, data.userSn)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
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
def get_user_info(userSn: str = Query(..., description="用户唯一标识（token）"), db: Session = Depends(get_db)):
    user = crud.get_user_by_sn(db, userSn)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
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
def save_settings(userSn: str = Query(..., description="用户唯一标识（token）"),
                  data: schemas.UserSettingSave = None,
                  db: Session = Depends(get_db)):
    user = crud.get_user_by_sn(db, userSn)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
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


# -------------------------- 排行榜接口 --------------------------
@app.get("/api/ranking", summary="获取排行榜")
def get_ranking(province: str = Query(None, description="省份名称（不传则返回全国排行）"),
                limit: int = Query(100, description="返回数量"),
                db: Session = Depends(get_db)):
    if province:
        users = crud.get_province_ranking(db, province, limit)
    else:
        users = crud.get_nationwide_ranking(db, limit)

    ranking_list = []
    for rank, user in enumerate(users, 1):
        level = crud.get_level_by_merit(db, user.merit_count)
        ranking_list.append({
            "rank": rank,
            "userSn": user.user_sn,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "meritCount": user.merit_count,
            "province": user.province,
            "levelName": level.level_name if level else "初心者",
            "levelColor": level.color if level else "#9E9E9E",
        })

    return {
        "code": 200,
        "msg": "获取成功",
        "data": {
            "province": province,
            "list": ranking_list
        }
    }


# -------------------------- 功德等级列表接口 --------------------------
@app.get("/api/levels", summary="获取所有等级配置")
def get_levels(db: Session = Depends(get_db)):
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
def update_nickname(userSn: str = Query(..., description="用户唯一标识（token）"),
                    nickname: str = Query(..., description="新昵称"),
                    db: Session = Depends(get_db)):
    user = crud.get_user_by_sn(db, userSn)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not nickname or len(nickname) > 50:
        raise HTTPException(status_code=400, detail="昵称长度需在1-50字符之间")
    user.nickname = nickname
    db.commit()
    return {"code": 200, "msg": "更新成功", "data": {"nickname": nickname}}


# -------------------------- 更新省份接口 --------------------------
@app.post("/api/update-province", summary="更新用户所在省份")
def update_province(userSn: str = Query(..., description="用户唯一标识（token）"),
                    province: str = Query(..., description="省份名称"),
                    db: Session = Depends(get_db)):
    user = crud.get_user_by_sn(db, userSn)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    user.province = province
    db.commit()
    return {"code": 200, "msg": "更新成功", "data": {"province": province}}


# -------------------------- 启动入口 --------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)