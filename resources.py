from fastapi import APIRouter

# 子路由：所有皮肤/背景/资源接口都在这里
router = APIRouter()

# ===================== 背景资源 =====================
bg_resources = [
    {
        "id": "bg_01_v1",
        "name": "清晨",
        "url": "http://localhost/static/bg/bg_01_v1.jpg",
        "isDefault": True
    },
    {
        "id": "bg_02_v1",
        "name": "小径",
        "url": "http://localhost/static/bg/bg_02_v1.jpg",
        "isDefault": False
    },
    {
        "id": "bg_03_v1",
        "name": "夕阳",
        "url": "http://localhost/static/bg/bg_03_v1.jpg",
        "isDefault": False
    },
    {
        "id": "bg_04_v1",
        "name": "山村",
        "url": "http://localhost/static/bg/bg_04_v1.jpg",
        "isDefault": False
    },
    {
        "id": "bg_05_v1",
        "name": "竹林",
        "url": "http://localhost/static/bg/bg_05_v1.jpg",
        "isDefault": False
    }
]

# ===================== 木鱼资源 =====================
muyu_resources = [
    {
        "id": "muyu_01_v1",
        "name": "经典木鱼",
        "url": "",
        "isDefault": True
    },
    {
        "id": "muyu_02_v1",
        "name": "发财木鱼",
        "url": "http://localhost/static/muyu/muyu_02_v1.png",
        "isDefault": False
    }
]

# ===================== 木槌资源 =====================
hammer_resources = [
    {
        "id": "hammer_01_v1",
        "name": "经典木槌",
        "url": "",
        "isDefault": True
    }
]

# ===================== 底座资源 =====================
base_resources = [
    {
        "id": "base_01_v1",
        "name": "经典底座",
        "url": "",
        "isDefault": True
    }
]

# ===================== 音效资源 =====================
sound_resources = [
    {
        "id": "sound_01_v1",
        "name": "经典音效",
        "url": "",
        "isDefault": True
    }
]

# ===================== 统一资源接口 =====================
@router.get("/api/resources")
def get_resources(t: str):
    if t == "bg":
        return {"code": 0, "data": bg_resources}
    if t == "muyu":
        return {"code": 0, "data": muyu_resources}
    if t == "hammer":
        return {"code": 0, "data": hammer_resources}
    if t == "base":
        return {"code": 0, "data": base_resources}
    if t == "sound":
        return {"code": 0, "data": sound_resources}
    return {"code": -1, "msg": "类型错误"}