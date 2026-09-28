from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from deps import get_current_user, get_session
from db.models import User
from schemas.chat import (
    SessionItem,
    SessionListResponse,
    MessageItem,
    SessionDetailResponse,
    ChatRequest,
    ChatResponse,
    SourceItem,
)
from db.models import Session
from sqlalchemy import select
from services.chat import (
    create_session,
    get_user_sessions,
    delete_session,
    get_session_detail,
    process_question,
)

from sse_starlette.sse import EventSourceResponse  # fastapi 进行sse协议响应
import asyncio

SYSTEM_PROMPT = """你是一个校园生活助手，请严格遵循以下规则：

1. 仅基于提供的上下文内容回答问题
2. 如果上下文不足以回答，如实说明"文档中没有相关信息"，不要编造
3. 使用中文回答，语言简洁易懂
4. 涉及数字、时间、地点等信息时，引用原文

上下文：
{context}"""

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", status_code=201)
async def new_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):

    session = await create_session(user_id=str(current_user.id), db=db)

    return {"session_id": str(session.id), "title": session.title}


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):

    sessions = await get_user_sessions(user_id=str(current_user.id), db=db)

    session_items = []
    for session in sessions:
        session_item = SessionItem(
            id=str(session.id), title=session.title, created_at=session.created_at
        )
        session_items.append(session_item)

    return SessionListResponse(sessions=session_items)


# RESTful API
@router.delete("/sessions/{session_id}")
async def remove_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):

    await delete_session(session_id=session_id, db=db)

    return {"message": "Session deleted"}


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):

    messages = await get_session_detail(session_id, db)

    messages = [
        MessageItem(
            role=m.role,
            content=m.content,
            sources=m.sources,
            created_at=m.created_at,
        )
        for m in messages
    ]

    return SessionDetailResponse(messages=messages)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    response = await process_question(
        question=request.question, session_id=request.session_id, db=db
    )
    answer = response.get("answer")
    sources = response.get("sources", [])

    source_items = [
        SourceItem(
            chapter=s.get("chapter"),
            section=s.get("section"),
            content=s.get("content"),
            score=s.get("score"),
        )
        for s in sources
    ]

    return ChatResponse(answer=answer, sources=source_items)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    流式问答 : SSE协议
    token 形式返回llm结果 实现前端打字机效果

    # token 事件：llm 文本片段
    # source事件：来源
    # done事件：完成

    """
    question = request.question
    session_id = request.session_id

    async def stream_event_generator(question, session_id, db: AsyncSession):
        from rag.retriever import retrieve
        from rag.llm import get_llm
        from langchain_core.prompts import ChatPromptTemplate

        # 检索
        docs_str, sources = retrieve(question)

        #  获取大模型
        print("获取大模型")
        llm = get_llm()

        print("构建提示词")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "{input}"),
            ]
        )

        chain = prompt | llm

        # 返回值：AsyncIterator

        # llm 每次生成一个token也叫chunk
        answer_parts = []
        async for chunk in chain.astream({"context": docs_str, "input": question}):

            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            if content:
                # 追加到answer_parts列表
                answer_parts.append(content)

                # 通过SSE 推送给前端
                yield {"data": {"type": "token", "content": content}}

        # 返回检索来源
        yield {"data": {"type": "source", "sources": sources}}

        # 标记流结束
        yield {"data": {"type": "done"}}

        # 异步保存 llm流式回答消息 到数据库
        #  ensure_future ：后台执行 不阻塞SSE 响应返回
        print(f"----------------{answer_parts}")
        asyncio.ensure_future(
            _save_message_ai(
                session_id=session_id,
                question=question,
                answer="".join(answer_parts),
                sources=sources,
            )
        )
        asyncio.ensure_future(
            _save_message_user(session_id=session_id, question=question),
        )

    # EventSourceResponse 将生成器包装为 SSE 响应
    return EventSourceResponse(
        stream_event_generator(question=question, session_id=session_id, db=db)
    )


async def _save_message_user(session_id: str, question: str):
    from db.sessions_async import async_session_factory
    from db.models import Message

    async with async_session_factory() as db:
        user_message = Message(
            session_id=session_id,
            content=question,
            role="user",
        )

        db.add(user_message)
        await db.commit()


async def _save_message_ai(session_id: str, question: str, answer: str, sources: list):
    from db.sessions_async import async_session_factory
    from db.models import Message

    async with async_session_factory() as db:

        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=sources,
        )
        db.add(assistant_msg)
        await db.commit()

        # 会话标题修改
        session_result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        if session and session.title == "新对话":
            session.title = question[:10]
            await db.commit()
