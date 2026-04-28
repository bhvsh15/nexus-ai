from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class CrewAgent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    role: str
    goal: str
    backstory: str
    model: str
    tools: str  # JSON string of tools configuration
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    description: str | None = None

class CrewTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    expected_output: str | None = None
    agent_id: int = Field(foreign_key="crewagent.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Crew(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    process: str
    agent_ids: str  # JSON string of agent IDs in the crew
    task_ids: str  # JSON string of task IDs associated with the crew
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CrewRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    crew_id: int = Field(foreign_key="crew.id")
    input: str
    output: str | None = None
    status: str = "running"  # running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


    