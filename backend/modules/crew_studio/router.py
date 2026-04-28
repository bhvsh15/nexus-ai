from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from typing import Annotated
from core.database import get_session
from . import service
from .models import CrewAgent, CrewTask, Crew, CrewRun

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

class CreateAgentRequest(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    model: str = "llama3.2"
    tools: list[str] = []

class CreateTaskRequest(BaseModel):
    description: str
    expected_output: str
    agent_id: int

class CreateCrewRequest(BaseModel):
    name: str
    process: str = "sequential"
    agent_ids: list[int]
    task_ids: list[int]

class RunCrewRequest(BaseModel):
    input: str

@router.post("/agents", response_model=CrewAgent)
def create_crew_agent(body: CreateAgentRequest, session: SessionDep):
    return service.create_crew_agent(session, body.name, body.role, body.goal, body.backstory, body.model, body.tools)

@router.get("/agents", response_model=list[CrewAgent])
def get_all_crew_agents(session: SessionDep):
    return service.get_all_crew_agents(session)

@router.post("/tasks", response_model=CrewTask)
def create_task(body: CreateTaskRequest, session: SessionDep):
    return service.create_task(session, body.description, body.expected_output, body.agent_id)

@router.get("/tasks", response_model=list[CrewTask])
def get_all_tasks(session: SessionDep):
    return service.get_all_tasks(session)

@router.post("/crews", response_model=Crew)
def create_crew(body: CreateCrewRequest, session: SessionDep):
    return service.create_crew(session, body.name, body.process, body.agent_ids, body.task_ids)

@router.get("/crews", response_model=list[Crew])
def get_all_crews(session: SessionDep):
    return service.get_all_crews(session)

@router.get("/crews/{crew_id}", response_model=Crew)
def get_crew(crew_id: int, session: SessionDep):
    crew = service.get_crew(session, crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    return crew

@router.post("/crews/{crew_id}/run", response_model=CrewRun)
def run_crew(crew_id: int, body: RunCrewRequest, session: SessionDep):
    try:
        return service.run_crew(session, crew_id, body.input)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
