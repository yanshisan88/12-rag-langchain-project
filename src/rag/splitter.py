from langchain_text_splitters import MarkdownHeaderTextSplitter,RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split(markdown_document: str) -> list[Document]:

    # 按章节分割
    headers_to_split_on = [
        ("##", "chapter"),
        ("###", "section")
    ]
    # 配置MarkdownHeaderTextSplitter  按章节分割 
    # markdown_splitter 切割工具
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    md_docs = markdown_splitter.split_text(markdown_document)


    # 按段落划分
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=30,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],  # 优先级
    )
    # text_splitter 切割工具
    chunks = text_splitter.split_documents(md_docs)

    return chunks

    
