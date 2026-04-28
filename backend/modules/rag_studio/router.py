from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from typing import Annotated
from core.database import get_session
from . import service
from .models import Pipeline
from pydantic import BaseModel
import shutil

class CreatePipelineRequest(BaseModel):
    name: str
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "nomic-embed-text"

class QueryRequest(BaseModel):
    question: str
    model: str = "llama3.2:1b"

router = APIRouter(tags=["RAG Studio"])

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/pipelines", response_model=Pipeline)
def create_pipeline(request: CreatePipelineRequest, session: Annotated[Session, Depends(get_session)]):
    return service.create_pipeline(session, request.name, request.chunk_size, request.chunk_overlap, request.embedding_model)

@router.get("/pipelines/{pipeline_id}", response_model=Pipeline)
def get_pipeline(pipeline_id: int, session: Annotated[Session, Depends(get_session)]):
    pipeline = service.get_pipeline(session, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline

@router.get("/pipelines", response_model=list[Pipeline])
def get_all_pipelines(session: SessionDep):
    return service.get_all_pipelines(session)

@router.post("/pipelines/{pipeline_id}/ingest")
async def ingest_document(pipeline_id: int, session: SessionDep, file: UploadFile = File(...)):
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return service.ingest_document(session, pipeline_id, file_location, file.filename, file.filename.split(".")[-1])

@router.post("/pipelines/{pipeline_id}/query")
async def query_pipeline(pipeline_id: int, request: QueryRequest, session: SessionDep):
    pipeline = service.get_pipeline(session, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return service.query_pipeline(session, pipeline_id, request.question, request.model)
