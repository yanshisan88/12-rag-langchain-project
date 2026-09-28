from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Session
from sqlalchemy import select
from db.models import Message
from rag.generation import ask_question
async def create_session(user_id: str, db: AsyncSession) -> Session:
    session = Session(
        user_id=user_id
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_user_sessions(user_id: str, db: AsyncSession) -> list[Session]:

    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.created_at.desc())
    )

    return list(result.scalars().all())

async def delete_session(session_id: str, db: AsyncSession):
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
    )

    session = result.scalar_one_or_none()

    if session:
        await db.delete(session) # 注意 ：关联消息 已经做的级联删除
        await db.commit()

# 获取session详情 ： 消息列表
async def get_session_detail(session_id: str, db: AsyncSession):
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
    )

    return list(result.scalars().all())

async def process_question(
        question: str, # 问题
        session_id: str, # 会话session_id
        db: AsyncSession, # db
):
    print(f"process_question---{question}")
    # 先把用户消息存储到数据库中
    user_message = Message(
        content=question,
        role="user",
        session_id=session_id,
    )
    db.add(user_message)
    await db.commit()


    # 数据库中历史消息
    history = await get_session_detail(
        session_id,
        db,
    )

    # 清除：大模型要的消息形式 {role: "user", content: "xxx"}
    history_messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in history[:-1] # 去掉最后一条消息
    ]


    # rag 问题： 检索 + 生成
    response = await ask_question(question, history_messages)
    answer = response["answer"]
    sources = response.get("sources",[])

    # 存储AI消息到数据库
    ai_msg = Message(
        session_id=session_id,
        role="assistant",
        content=answer,
        sources=sources,
    )
    db.add(ai_msg)
    await db.commit()

    # 会话标题修改
    session_result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if session and session.title == "新对话":
        session.title = question[:10]
        await db.commit()

    return response

