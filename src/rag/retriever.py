from rag.store import get_vector_store
from config import setting


def retrieve(question: str) -> tuple[str, list]:
    print(f"检索的question:{question}")
    vector_store = get_vector_store()

    # 返回值 list[tuple[Document, float]]
    docs_with_scores = vector_store.similarity_search_with_score(
        question, k=setting.RETRIEVER_TOP_K
    )

    
    docs_text = ''
    sources = []
    for doc, score in docs_with_scores:
        docs_text += f"{doc.page_content}\n"
        source = {
            "content": doc.page_content[:30], 
            "score": round(score,4),
            "chapter": doc.metadata.get("chapter", ""),  # 所属章节
            "section": doc.metadata.get("section", ""),  # 所属小节
        }
        sources.append(source)


    return  (docs_text, sources)