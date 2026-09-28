from qdrant_client import QdrantClient
from config import setting
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Payload, PointStruct, VectorParams, Distance
from rag.embedding import get_embedding
from pathlib import Path


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=setting.QDRANT_HOST,
        port=setting.QDRANT_PORT,
    )


def get_vector_store() -> QdrantVectorStore:

    client = get_qdrant_client()

    # 检查是否存在集合
    if not client.collection_exists(setting.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=setting.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=setting.QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    embedding = get_embedding()

    return QdrantVectorStore(
        client=client, collection_name=setting.QDRANT_COLLECTION, embedding=embedding
    )

def store_document(file_path: str) -> dict:
    from rag.loader import load
    from rag.splitter import split
     # 文档加载器
    doc_str = load(file_path)
    print(f"文档长度:{len(doc_str)}")
    # 文档分割器
    chunks = split(doc_str)
    print(f"分块后的文档长度:{len(chunks)}")
    # 向量存储
    vector_store = get_vector_store()
    text = [chunk.page_content for chunk in chunks]
    metadata = [chunk.metadata for chunk in chunks]
    # ids = vector_store.add_documents(chunks)
    qdrant_ids = vector_store.add_texts(text, metadata) #异步添加
    print("文档已添加到向量数据库中")
    return {"qdrant_ids": qdrant_ids,"chunk_count":len(chunks),"chunks":chunks}
# if __name__ == "__main__":
   
    # base_path = Path(__file__).parent.parent.parent
    # file_path = base_path / "data" / "simple_university_doc.md"
    # result = store_document(str(file_path))
    # doc_str = load(file_path)
    # print(f"文档长度:{len(doc_str)}")

    # chunks = split(doc_str)
    # print(f"分块后的文档长度:{len(chunks)}")
    # # print(chunks)
    # vector_store = get_vector_store()
    # vector_store.add_documents(chunks)
    # print("文档已添加到向量数据库中")

    # cd src
    # uv run python -m src.rag.store

def delete_document_points(qdrant_ids: list[str]):
     client = get_qdrant_client()

     client.delete(
            collection_name=setting.QDRANT_COLLECTION,
            points_selector=qdrant_ids,
         )