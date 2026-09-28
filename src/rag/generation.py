from rag.llm import get_llm
from rag.retriever import retrieve
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from rag.store import get_vector_store
from rag.retriever import retrieve

SYSTEM_PROMPT = """你是一个校园生活助手，请严格遵循以下规则：

1. 仅基于提供的上下文内容回答问题
2. 如果上下文不足以回答，如实说明"文档中没有相关信息"，不要编造
3. 使用中文回答，语言简洁易懂
4. 涉及数字、时间、地点等信息时，引用原文

上下文：
{context}"""


async def ask_question(question: str, history: list | None = None) -> dict:

    #  获取大模型
    print("获取大模型")
    llm = get_llm()

    # 检索信息
    docs_text, sources = retrieve(question)

    # 构建提示词
    print("构建提示词")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(
                variable_name="chat_history", optional=True
            ),  # 聊天历史 可选
            ("human", "{input}"),
        ]
    )

    #  定义链 ： dict ->prompt -> llm ->解析 -> anwser
    chain = prompt | llm | StrOutputParser()

    print("执行链:prompt | llm | StrOutputParser")
    answer = await chain.ainvoke(
        {"context": docs_text, "input": question, "chat_history": history or []}
    )

    print(f"生成的答案:", answer)
    print(f"来源文档:", sources)

    return {"answer": answer, "sources": sources}

# sse 事件生成器 ： 核心处理流式逻辑

if __name__ == "__main__":

    question = "宿舍几点关门?"

    ask_question(question=question)

    # asyncio.run(ask_question(query=query))

    # cd 项目根目录
    # uv run python -m src.rag.generation
