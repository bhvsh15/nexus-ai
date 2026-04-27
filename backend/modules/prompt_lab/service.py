from sqlmodel import Session, select
from .models import Prompt, PromptVersion, EvalRun
from datetime import datetime
from jinja2 import Template
from core.ollama_client import chat
import json

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

def render_prompt(content: str, input_variables: dict) -> str:
    template = Template(content)
    return template.render(**input_variables)

def judge_output(rendered_prompt: str, output: str) -> tuple[float, str]:
    judge_prompt = f"""You are an evaluator. Rate the quality of this response from 0.0 to 1.0.
Reply in this exact format:
SCORE: 0.8
REASON: The response was clear and accurate.

Prompt: {rendered_prompt}
Response: {output}"""

    response = chat(model="gemma4:e2b", messages=[{"role": "user", "content": judge_prompt}])
    text = response.message.content

    score = 0.5
    reason = ""
    for line in text.strip().split("\n"):
        if line.startswith("SCORE:"):
            try:
                score = float(line.split(":")[1].strip())
            except ValueError:
                pass
        elif line.startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()

    return score, reason


def get_production_version(session: Session, prompt_name: str) -> PromptVersion | None:
    prompt = session.exec(select(Prompt).where(Prompt.name == prompt_name)).first()
    if not prompt:
        return None
    return session.exec(
        select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt.id)
        .where(PromptVersion.stage == "production")
        .order_by(PromptVersion.version_number.desc())
    ).first()


def run_eval(session: Session, version_id: int, variables: dict, model: str) -> EvalRun:
    version = session.get(PromptVersion, version_id)
    if not version:
        raise ValueError("PromptVersion not found")

    rendered = render_prompt(version.content, variables)
    response = chat(model=model, messages=[{"role": "user", "content": rendered}])
    output = response.message.content

    score, reason = judge_output(rendered, output)

    eval_run = EvalRun(
        prompt_version_id=version_id,
        input_variables=json.dumps(variables),
        rendered_prompt=rendered,
        output=output,
        score=score,
        score_reason=reason
    )
    session.add(eval_run)
    session.commit()
    session.refresh(eval_run)
    return eval_run
