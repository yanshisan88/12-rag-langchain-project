from langchain_community.document_loaders import TextLoader
from pathlib import Path
from langchain_core.documents import Document


def load(file_path: str) -> str:

    loader = TextLoader(file_path,encoding="utf-8")
    documents = loader.load() 

    # contents = [doc.page_content for doc in documents]

    return documents[0].page_content


