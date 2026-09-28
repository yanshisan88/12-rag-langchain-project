from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from dotenv import load_dotenv
from config import setting
from sqlalchemy.orm import DeclarativeBase
from db.models import Base
class Base(DeclarativeBase):
    pass
DEBUG = setting.DEBUG
db_url = setting.DATABASE_URL
engine = create_engine(
    url=db_url,
    echo=True, #开启SQLAlchemy的日志输出 =>SQL 会打印到控制台
)

# 会话工厂（用于创建数据库会话）
SessionLocal = sessionmaker(engine)

# session 依赖函数
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    """初始化数据库：创建所有表"""
    with engine.begin() as conn:
        # 所有继承Base的模型=>通过engine =>生成表
        Base.metadata.create_all(bind=engine)
        # await conn.run_sync(Base.metadata.create_all)
        print("初始化数据库成功")

def close_db():
    """关闭数据库连接"""
    engine.dispose()
    print("关闭数据库连接成功")