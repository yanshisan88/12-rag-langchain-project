from fastapi import FastAPI
from config import setting
from fastapi.middleware.cors import CORSMiddleware
from db.sessions_async import init_db, close_db
from contextlib import asynccontextmanager
from fastapi import APIRouter
from api.auth import router as auth_router
from api.chat import router as chat_router
from api.document import router as document_router
# from api.system import router as system_router

# lifespan 是FastAPI生命周期的钩子
@asynccontextmanager
async def lifespan(app:FastAPI):
    """应用生命周期管理"""

    # 应用执行前初始化： 初始化数据库
    try:
        # 初始化数据库
        await init_db()
    except Exception as e:
        print(f"初始化数据库失败")
        print(e)
        raise e

    yield # 等待 fastapi 接受请求 服务器运行

    # 应用关闭后释放资源： 关闭数据库
    await close_db()

app = FastAPI(
    lifespan=lifespan,
    title = setting.APP_NAME,
    description = """This is a Campus RAG System""",
)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"], # 允许所有源访问
    allow_origins=["http://localhost:3000"], # 允许所有源访问
    allow_credentials=True, # 允许携带凭证
    allow_methods=["*"], # 允许所有请求方法  GET POST PUT DELETE OPTIONS
    # allow_methods=["GET"], # 允许GET请求方法
    allow_headers=["*"], # 允许所有请求头
)
root_router = APIRouter(prefix="/api/v1")
root_router.include_router(auth_router)
root_router.include_router(chat_router)
root_router.include_router(document_router)
app.include_router(root_router)

# root_router.include_router(system_router)
@app.get("/")
async def root():
    return {"message": "Hello"}