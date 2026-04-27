from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Prompt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PromptVersion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompt.id")
    version_number: int
    content: str
    stage: str = Field(default="draft")  # draft, staging, production
    commit_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EvalRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_version_id: int = Field(foreign_key="promptversion.id")
    input_variables: str  # JSON string of input variables
    rendered_prompt: str  # Prompt after Jinja rendering
    output: str
    score: float | None = None
    score_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    