from fastapi import APIRouter, Request

# 子路由：所有皮肤/背景/资源接口都在这里
router = APIRouter()

# ===================== 资源模板（url 为相对路径） =====================
bg_templates = [
    {"id": "bg_01", "name": "清晨", "url": "/static/bg/bg_01_v1.jpg", "isDefault": True},
    {"id": "bg_02", "name": "小径", "url": "/static/bg/bg_02_v1.jpg", "isDefault": False},
    {"id": "bg_03", "name": "夕阳", "url": "/static/bg/bg_03_v1.jpg", "isDefault": False},
    {"id": "bg_04", "name": "山村", "url": "/static/bg/bg_04_v1.jpg", "isDefault": False},
    {"id": "bg_05", "name": "竹林", "url": "/static/bg/bg_05_v1.jpg", "isDefault": False},
]

muyu_templates = [
    {"id": "fish_01", "name": "招财木鱼", "url": "/static/muyu/fish_01_v1.png", "isDefault": True},
    {"id": "muyu_02", "name": "经典款", "url": "/static/muyu/fish_02_v1.png", "isDefault": False},
    {"id": "muyu_03", "name": "花雕款", "url": "/static/muyu/fish_03_v1.png", "isDefault": False},
    {"id": "muyu_04", "name": "简朴款", "url": "/static/muyu/fish_04_v1.png", "isDefault": False},
    {"id": "muyu_05", "name": "梨花木", "url": "/static/muyu/fish_05_v1.png", "isDefault": False},
]

hammer_templates = [
    {"id": "hammer_01", "name": "桃心木槌", "url": "/static/hammer/hammer_01_v1.png", "isDefault": True},
    {"id": "hammer_02", "name": "柚木圆白", "url": "/static/hammer/hammer_02_v1.png", "isDefault": False},
    {"id": "hammer_03", "name": "红檀圆白", "url": "/static/hammer/hammer_03_v1.png", "isDefault": False},
    {"id": "hammer_04", "name": "圆头榉木", "url": "/static/hammer/hammer_04_v1.png", "isDefault": False},
]

base_templates = [
    {"id": "base_01", "name": "经典底座", "url": "/static/base/zuowei_01_v1.png", "isDefault": True},
    {"id": "base_02", "name": "金叶吉祥", "url": "/static/base/zuowei_02_v1.png", "isDefault": False},
    {"id": "base_03", "name": "金丝绣花", "url": "/static/base/zuowei_03_v1.png", "isDefault": False},
]

sound_templates = [
    {"id": "knock_01", "name": "圆润", "url": "/static/sound/knock_01_v1.mp3", "isDefault": True},
    {"id": "knock_02", "name": "沙哑", "url": "/static/sound/knock_02_v1.mp3", "isDefault": True},
    {"id": "knock_03", "name": "低沉", "url": "/static/sound/knock_03_v1.mp3", "isDefault": True},
]

# ===================== 统一资源接口 =====================
@router.get("/api/resources")
def get_resources(t: str, request: Request):
    # 根据请求的 scheme + host 构建 base URL（不含端口，静态资源由 nginx 80 端口提供）
    base_url = f"{request.url.scheme}://{request.url.hostname}"

    def _with_base(items):
        return [{**item, "url": base_url + item["url"]} for item in items]

    if t == "bg":
        return {"code": 0, "data": _with_base(bg_templates)}
    if t == "muyu":
        return {"code": 0, "data": _with_base(muyu_templates)}
    if t == "hammer":
        return {"code": 0, "data": _with_base(hammer_templates)}
    if t == "base":
        return {"code": 0, "data": _with_base(base_templates)}
    if t == "sound":
        return {"code": 0, "data": _with_base(sound_templates)}
    return {"code": -1, "msg": "类型错误"}