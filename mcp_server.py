

from mcp.server import FastMCP
from src.rag.generation import ask_question
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              

# mcp实例
mcp = FastMCP(
    name="Campus RAG System",
    instructions="""你是一个 RAG 知识库助手，可以检索校园相关文档（宿舍、食堂、选课、图书馆等）。

    工具：
    - rag_query      向知识库提问，返回基于检索增强生成的回答
   - list_documents  列出知识库中所有文档
    """,
)


@mcp.tool(name="rag_query", description="向知识库提问，返回基于检索增强生成的回答")
async def rag_query(question: str) -> dict:
    if not question.strip():
        return {"answer": "请输入有效问题。", "sources": []}
    try:
        response = await ask_question(question)  
        answer = response["answer"]
        sources = response["sources"]
        return {"answer": answer, "sources": sources}
    except Exception as e:
        return {"answer": f"查询出错：{str(e)}", "sources": []}
if __name__ == "__main__":
    mcp.run() 