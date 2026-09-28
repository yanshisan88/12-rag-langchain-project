from datetime import datetime, timedelta, timezone
from config import setting
from jose import jwt, JWTError


def create_access_token(data: dict[str, any]) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    to_encode.update({"type": "access"})

   #    timedelta ： 间隔时间
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    # jwt.encode(payload, key, algorithm)
    return jwt.encode(to_encode, setting.JWT_SECRET_KEY, setting.JWT_ALGORITHM)

def create_refresh_token(data: dict[str, str]) -> str:
    """创建刷新令牌"""

    to_encode = data.copy()

    to_encode.update({"type": "refresh"})

    expire = datetime.now(timezone.utc) + timedelta(
        days=setting.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({"exp": expire})

    # 编码 JWT
    return jwt.encode(
        to_encode,
        setting.JWT_SECRET_KEY,
        algorithm=setting.JWT_ALGORITHM,
    )


def verify_token(token: str) -> dict[str, str]:
    """验证令牌"""

    try:
        # 解码 JWT
        payload = jwt.decode(
            token,
            setting.JWT_SECRET_KEY,
            algorithms=[setting.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise ValueError("无效的令牌或者过期")
