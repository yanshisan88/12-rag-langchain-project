from fastapi import  Depends, status, HTTPException

from db.sessions_async import get_session
from sqlalchemy.orm import Session
from db.models import User

from sqlalchemy import select
from utils.jwt import  verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# 验证用户是否登录
# 获取当前用户: 获取用户传递token ,验证token ,获取用户信息
async def get_current_user(
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    session: Session = Depends(get_session),
):

    # 获取token &
    access_token = authorization.credentials

    # 验证token
    try:
        payload = verify_token(access_token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except ValueError:  # 验证失败
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    # 获取用户id
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 查询数据库中查询用户
    result = await session.execute(select(User).where(User.id == user_id))
    # 返回结果是一个对象  要么是用户对象，要么是None
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if user.is_active == False:  # 账号被禁用
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not admin",
        )
    return current_user
