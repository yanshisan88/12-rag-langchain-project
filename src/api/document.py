from fileinput import filename
from db.models import User

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.sessions_async import get_session
from deps import get_current_user
from services.document import (
    list_documents,
    upload_document,
)
from services.document import (
    delete_document
)
from schemas.document import (
    DocumentItem,
    DocumentListResponse,
    DocumentReindexResponse,
    DocumentUploadResponse,
)
from deps import get_admin_user

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload(
    file: UploadFile = File(...),  # ... 必须
    db: AsyncSession = Depends(get_session),
    user: str = Depends(get_current_user),
):

    # 校验：文件类型  .md  .txt
    if not file.filename.endswith((".md", ".txt")):
        raise HTTPException(
            status_code=400, detail="Only .md and .txt files are supported"
        )

    # 校验：文件大小
    filesize = file.size
    if filesize > 1024 * 1024 * 10:  # 10M
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")

    # 读文件bytes
    content = await file.read()

    # 调用service层
    try:
        doc = await upload_document(
            filename=file.filename,
            content=content,
            user_id=str(user.id),
            db=db,
        )
    except Exception as e:  # 捕获所有异常
        raise HTTPException(status_code=503, detail=f"upload document error:{str(e)}")

    # 响应结果

    return DocumentUploadResponse(
        id=str(doc.id),
        name=doc.filename,
        status=doc.status,
        chunk_count=doc.chunk_count,
    )

@router.get("", response_model=DocumentListResponse)
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)):

     docs = await list_documents(
         db
     )

     documents = []

     for doc in docs:
         documents.append(
             DocumentItem(
                 id=str(doc.id),
                 name=doc.filename,
                 status=doc.status,
                 chunk_count=doc.chunk_count,
                 file_size=doc.file_size,
                 created_at=doc.created_at,
             )
         )

     return DocumentListResponse(
        documents=documents
     )

@router.delete("/{document_id}")
async def delete(
    document_id: str, 
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_session)):

    await delete_document(document_id, db)

    return {"message": "delete success"}