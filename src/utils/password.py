import bcrypt


# 密码加密
def get_password_hash(password: str) -> str:
    # password.encode('utf-8') : 将字符串转换为字节码
    # bcrypt.gensalt() : 生成盐
    # bcrypt.hashpw() : 加密
    # decode("utf-8") : 将字节码转换为字符串
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")


# 密码验证
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # plain_password : 明文密码
    # hashed_password : 密文密码
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
