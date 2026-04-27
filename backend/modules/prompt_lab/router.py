from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Annotated
from core.database import get_session
from . import service
from .models import Prompt, PromptVersion
from pydantic import BaseModel

class CreatePromptRequest(BaseModel):
    name: str
    description: str = ""

class CommitVersionRequest(BaseModel):
    content: str
    commit_message: str = ""

class PromoteRequest(BaseModel):
    stage: str


router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/prompts", response_model=Prompt)
def create_prompt(request: CreatePromptRequest, session: SessionDep):
    return service.create_prompt(session, request.name, request.description)

@router.get("/prompts", response_model=list[Prompt])
def read_prompts(session: SessionDep):
    return service.get_all_prompts(session)

@router.get("/prompts/{prompt_id}", response_model=Prompt)
def read_prompt(prompt_id: int, session: SessionDep):
    prompt = service.get_prompt_by_id(session, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.post("/prompts/{prompt_id}/versions", response_model=PromptVersion)
def commit_prompt_version(prompt_id: int, request: CommitVersionRequest, session: SessionDep):
    return service.commit_version(session, prompt_id, request.content, request.commit_message)

@router.get("/prompts/{prompt_id}/versions", response_model=list[PromptVersion])
def read_prompt_versions(prompt_id: int, session: SessionDep):
    return service.get_versions(session, prompt_id)

@router.patch("/prompts/{prompt_id}/versions/{version_id}/promote", response_model=PromptVersion)
def promote_prompt_version(version_id: int, body: PromoteRequest, session: SessionDep):
    return service.promote_version(session, version_id, body.stage)
