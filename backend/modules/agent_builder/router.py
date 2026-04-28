from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Annotated
from pydantic import BaseModel
from core.database import get_session
from . import service
from .models import Agent, AgentRun, AgentRunStep
import json

router = APIRouter(tags=["Agent Builder"])

SessionDep = Annotated[Session, Depends(get_session)]

class CreateAgentRequest(BaseModel):
    name: str
    description: str | None = None
    model: str = "llama3.2"
    tools: list[str] = []

@router.post("/agents", response_model=Agent)
def create_agent(body: CreateAgentRequest, session: SessionDep):
    return service.create_agent(session, body.name, body.description, body.model, body.tools)

@router.get("/agents", response_model=list[Agent])
def get_all_agents(session: SessionDep):
    return service.get_all_agents(session)

@router.get("/agents/{agent_id}", response_model=Agent)
def get_agent(agent_id: int, session: SessionDep):
    agent = service.get_agent(session, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/agents/{agent_id}/runs/{run_id}", response_model=AgentRun)
def get_run(agent_id: int, run_id: int, session: SessionDep):
    run = service.get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.get("/agents/{agent_id}/runs/{run_id}/steps", response_model=list[AgentRunStep])
def get_run_steps(agent_id: int, run_id: int, session: SessionDep):
    return service.get_run_steps(session, run_id)

@router.get("/agents/{agent_id}/run")
async def run_agent(agent_id: int, input: str, session: SessionDep):
    async def event_stream():
        async for chunk in service.run_agent(session, agent_id, input):
            yield f"data: {json.dumps(chunk)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
