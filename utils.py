import random
import string
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os

# 加载环境变量（指定UTF-8编码，避免解码错误）
load_dotenv(encoding="utf-8")


# -------------------------- userSn 生成（严格遵循16位规范） --------------------------
def generate_user_sn() -> str:
    """生成16位唯一userSn：U + 15位大写字母+数字，AI编程无需修改"""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choice(chars) for _ in range(15))
    return f"U{suffix}"


# -------------------------- 功德提交限流（高并发适配） --------------------------
last_commit_time = {}  # 全局记录：userSn -> 最后一次提交时间


def check_commit_interval(user_sn: str, is_auto: bool = False) -> bool:
    """校验批量提交间隔：手动4秒，自动5秒"""
    now = datetime.now().timestamp()
    interval = 5 if is_auto else 4
    if user_sn not in last_commit_time:
        last_commit_time[user_sn] = now
        return True
    if now - last_commit_time[user_sn] >= interval:
        last_commit_time[user_sn] = now
        return True
    return False


def check_commit_count(count: int, is_auto: bool = False) -> int:
    """校验提交次数上限：手动50次，自动20次"""
    max_count = 20 if is_auto else 50
    return min(count, max_count)


# -------------------------- 短信模拟（本地开发专用） --------------------------
phone_verify_code = {}  # 全局记录：手机号 -> 验证码信息


def send_verify_code(phone: str) -> bool:
    """本地模拟发送验证码，固定123456，不调用真实接口"""
    # 手机号格式校验
    if not (len(phone) == 11 and phone.startswith('1') and phone.isdigit()):
        return False
    # 发送频率校验（每分钟1次，每日10次）
    now = datetime.now()
    if phone in phone_verify_code:
        code_info = phone_verify_code[phone]
        if now - code_info["create_time"] < timedelta(minutes=1):
            return False
        if code_info["send_count"] >= 10:
            return False
        phone_verify_code[phone]["send_count"] += 1
    else:
        phone_verify_code[phone] = {
            "code": "123456",
            "create_time": now,
            "send_count": 1
        }
    print(f"[本地模拟短信] 手机号：{phone}，验证码：123456")
    return True


def verify_code(phone: str, code: str) -> bool:
    """本地模拟校验：任意6位数字即通过"""
    if len(code) == 6 and code.isdigit():
        if phone in phone_verify_code:
            del phone_verify_code[phone]
        return True
    return False


# -------------------------- 微信授权（适配测试号，规避报错） --------------------------
def get_wechat_openid(code: str) -> dict:
    """通过微信授权code获取openid、昵称、头像，适配本地测试号"""
    # 读取微信配置（从.env获取，避免硬编码）
    wechat_appid = os.getenv("WECHAT_APPID")
    wechat_appsecret = os.getenv("WECHAT_APPSECRET")
    wechat_auth_url = os.getenv("WECHAT_AUTH_URL")
    wechat_user_info_url = os.getenv("WECHAT_USER_INFO_URL")

    # 校验配置完整性（规避41002报错：appid missing）
    if not all([wechat_appid, wechat_appsecret, wechat_auth_url, wechat_user_info_url]):
        print("微信配置未完善，请检查.env文件")
        return {}

    # 第一步：获取access_token和openid
    auth_params = {
        "appid": wechat_appid,
        "secret": wechat_appsecret,
        "code": code,
        "grant_type": "authorization_code"
    }
    try:
        auth_response = requests.get(wechat_auth_url, params=auth_params, timeout=5)
        auth_data = auth_response.json()
        if "errcode" in auth_data and auth_data["errcode"] != 0:
            print(f"微信授权失败：{auth_data['errmsg']}")
            return {}
        access_token = auth_data.get("access_token")
        openid = auth_data.get("openid")
        if not (access_token and openid):
            print("未获取到openid和access_token")
            return {}
    except Exception as e:
        print(f"微信授权接口请求失败：{e}")
        return {}

    # 第二步：获取用户信息（规避41001报错：access_token missing）
    user_info_params = {
        "access_token": access_token,
        "openid": openid,
        "lang": "zh_CN"
    }
    try:
        user_info_response = requests.get(wechat_user_info_url, params=user_info_params, timeout=5)
        user_info_data = user_info_response.json()
        if "errcode" in user_info_data and user_info_data["errcode"] != 0:
            print(f"获取用户信息失败：{user_info_data['errmsg']}")
            return {"openid": openid}
        return {
            "openid": openid,
            "nickname": user_info_data.get("nickname"),
            "avatar": user_info_data.get("headimgurl")
        }
    except Exception as e:
        print(f"获取用户信息接口失败：{e}")
        return {"openid": openid}