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
        "id": "fish_01_v1",
        "name": "招财木鱼",
        "url": "http://localhost/static/muyu/fish_01_v1.png",
        "isDefault": True
    },
    {
        "id": "muyu_02_v1",
        "name": "经典款",
        "url": "http://localhost/static/muyu/fish_02_v1.png",
        "isDefault": False
    },
    {
        "id": "muyu_03_v1",
        "name": "花雕款",
        "url": "http://localhost/static/muyu/fish_03_v1.png",
        "isDefault": False
    },
    {
        "id": "muyu_04_v1",
        "name": "简朴款",
        "url": "http://localhost/static/muyu/fish_04_v1.png",
        "isDefault": False
    },
    {
        "id": "muyu_05_v1",
        "name": "梨花木",
        "url": "http://localhost/static/muyu/fish_05_v1.png",
        "isDefault": False
    }
]

# ===================== 木槌资源 =====================
hammer_resources = [
    {
        "id": "hammer_01_v1",
        "name": "桃心木槌",
        "url": "http://localhost/static/hammer/hammer_01_v1.png",
        "isDefault": True
    },
    {
        "id": "hammer_02_v1",
        "name": "柚木圆白",
        "url": "http://localhost/static/hammer/hammer_02_v1.png",
        "isDefault": False
    },
    {
        "id": "hammer_03_v1",
        "name": "红檀圆白",
        "url": "http://localhost/static/hammer/hammer_03_v1.png",
        "isDefault": False
    },
    {
        "id": "hammer_04_v1",
        "name": "圆头榉木",
        "url": "http://localhost/static/hammer/hammer_04_v1.png",
        "isDefault": False
    }
]

# ===================== 底座资源 =====================
base_resources = [
    {
        "id": "base_01_v1",
        "name": "经典底座",
        "url": "http://localhost/static/base/zuowei_01_v1.png",
        "isDefault": True
    },
    {
        "id": "base_02_v1",
        "name": "金叶吉祥",
        "url": "http://localhost/static/base/zuowei_02_v1.png",
        "isDefault": False
    },
    {
        "id": "base_03_v1",
        "name": "金丝绣花",
        "url": "http://localhost/static/base/zuowei_03_v1.png",
        "isDefault": False
    }
]

# ===================== 音效资源 =====================
sound_resources = [
    {
        "id": "knock_01_v1",
        "name": "圆润",
        "url": "http://localhost/static/sound/knock_01_v1.mp3",
        "isDefault": True
    },{
        "id": "knock_02_v1",
        "name": "沙哑",
        "url": "http://localhost/static/sound/knock_02_v1.mp3",
        "isDefault": True
    },
{
        "id": "knock_03_v1",
        "name": "低沉",
        "url": "http://localhost/static/sound/knock_03_v1.mp3",
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