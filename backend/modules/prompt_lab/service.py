from sqlmodel import Session,select
from .models import Prompt, PromptVersion
from datetime import datetime

def create_prompt(session: Session, name: str, description: str = "") -> Prompt:
    prompt = Prompt(name=name, description=description)
    session.add(prompt)
    session.commit()
    session.refresh(prompt)
    return prompt

def get_all_prompts(session: Session) -> list[Prompt]:
    return session.exec(select(Prompt)).all()

def get_prompt_by_id(session: Session, prompt_id: int) -> Prompt | None:
    return session.get(Prompt, prompt_id)

def commit_version(session: Session, prompt_id: int, content: str, commit_message: str) -> PromptVersion:
    # Get the latest version number for the prompt
    latest_version = session.exec(
        select(PromptVersion).where(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number.desc())
    ).first()
    
    new_version_number = (latest_version.version_number + 1) if latest_version else 1
    
    new_version = PromptVersion(
        prompt_id=prompt_id,
        version_number=new_version_number,
        content=content,
        commit_message=commit_message,
        stage="draft"
    )
    
    session.add(new_version)
    session.commit()
    session.refresh(new_version)
    
    return new_version

def get_versions(session: Session, prompt_id: int) -> list[PromptVersion]:
    return session.exec(
        select(PromptVersion).where(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number.desc())
    ).all()

def get_version(session: Session, version_id: int) -> PromptVersion | None:
    return session.get(PromptVersion, version_id)

def promote_version(session: Session, version_id: int, target_stage: str) -> PromptVersion:
    version = session.get(PromptVersion, version_id)
    if not version:
        raise ValueError("PromptVersion not found")
    
    version.stage = target_stage
    version.updated_at = datetime.utcnow()
    
    session.add(version)
    session.commit()
    session.refresh(version)
    
    return version