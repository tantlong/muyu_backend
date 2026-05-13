from pydantic import BaseModel, Field, field_validator
from typing import Optional


# -------------------------- 短信验证码相关 --------------------------
class PhoneVerifyCode(BaseModel):
    """获取手机验证码请求模型"""
    phone: str = Field(..., description="手机号，11位数字")

    @field_validator('phone')
    @classmethod
    def phone_format_check(cls, v):
        if not (len(v) == 11 and v.startswith('1') and v.isdigit()):
            raise ValueError('手机号格式错误，需为11位数字且以1开头')
        return v


# -------------------------- 手机号登录/注册 --------------------------
class AppUserLogin(BaseModel):
    """手机号登录/注册请求模型（未注册则自动注册）"""
    phone: str = Field(..., description="手机号，11位数字")
    code: str = Field(..., description="6位数字验证码")

    @field_validator('phone')
    @classmethod
    def phone_format_check(cls, v):
        if not (len(v) == 11 and v.startswith('1') and v.isdigit()):
            raise ValueError('手机号格式错误')
        return v

    @field_validator('code')
    @classmethod
    def code_format_check(cls, v):
        if not (len(v) == 6 and v.isdigit()):
            raise ValueError('验证码格式错误，需为6位数字')
        return v


# -------------------------- 微信登录/捆绑 --------------------------
class WechatAuthCode(BaseModel):
    """微信授权请求模型（登录/捆绑用）"""
    code: str = Field(..., description="微信授权code，有效期5分钟")


class WechatBindRequest(BaseModel):
    """微信号捆绑请求模型（已登录用户捆绑微信）"""
    userSn: str = Field(..., description="用户唯一标识（token）")
    code: str = Field(..., description="微信授权code")


# -------------------------- 基础用户凭证（依赖注入复用） --------------------------
class BaseUserSn(BaseModel):
    """从请求体提取 userSn 的基类（供 FastAPI 依赖注入使用）"""
    userSn: str = Field(..., description="用户唯一标识（token）")


# -------------------------- 功德提交 --------------------------
class KnockSubmit(BaseModel):
    """功德敲击提交请求模型"""
    userSn: str = Field(..., description="用户唯一标识（token）")
    count: int = Field(..., description="敲击次数")
    isAuto: bool = Field(False, description="是否自动敲击")


# -------------------------- 个性化配置 --------------------------
class UserSettingSave(BaseModel):
    """保存个性化配置请求模型（不传则不更新）"""
    fishSkin: Optional[str] = None
    hammerSkin: Optional[str] = None
    knockSound: Optional[str] = None
    background: Optional[str] = None
    volume: Optional[int] = None
    isVibrate: Optional[int] = None
    autoFreq: Optional[int] = None
    autoDuration: Optional[int] = None


# -------------------------- 接口响应模型 --------------------------
class LoginResponse(BaseModel):
    """登录/注册响应模型"""
    code: int = Field(200, description="状态码")
    msg: str = Field(..., description="提示信息")
    data: dict = Field(..., description="用户信息：userSn、meritCount、levelName等")