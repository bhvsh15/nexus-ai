from sqlmodel import Session, select
from .models import Agent, AgentRun, AgentRunStep
from datetime import datetime
import json
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from typing import AsyncGenerator
from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def echo(message: str) -> str:
    """Echo the input message."""
    return message

TOOL_REGISTRY = {
    "calculate": calculate,
    "echo": echo
}

def create_agent(session: Session, name: str, description: str, model: str, tools: list[str]) -> Agent:
    agent = Agent(name=name, description=description, model=model, tools=json.dumps(tools))
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent

def get_agent(session: Session, agent_id: int) -> Agent | None:
    return session.get(Agent, agent_id)

def get_all_agents(session: Session) -> list[Agent]:
    return session.exec(select(Agent)).all()

def get_run(session: Session, run_id: int) -> AgentRun | None:
    return session.get(AgentRun, run_id)

def get_run_steps(session: Session, run_id: int) -> list[AgentRunStep]:
    return session.exec(select(AgentRunStep).where(AgentRunStep.run_id == run_id)).all()

async def run_agent(session: Session, agent_id: int, input: str) -> AsyncGenerator[dict, None]:
    agent = get_agent(session, agent_id)
    if not agent:
        raise ValueError("Agent not found")
    
    run = AgentRun(agent_id=agent_id, input=input, status="running")
    session.add(run)
    session.commit()
    session.refresh(run)

    
    tool_names = json.loads(agent.tools)
    tools = [TOOL_REGISTRY[t] for t in tool_names if t in TOOL_REGISTRY]
    llm = ChatOllama(model=agent.model)
    graph = create_react_agent(llm, tools)

    try:
        async for event in graph.astream({"messages": [("user", input)]}):
            for node,data in event.items():
                step = AgentRunStep(run_id=run.id, step_type=node, input=data.get("input", ""), output=data.get("output", ""), tool_name=data.get("tool_name"))
                session.add(step)
                session.commit()
                session.refresh(step)
                yield {"node": node, "data": str(data)}
            
        run.status = "completed"
        run.output = str(data)
        run.updated_at = datetime.utcnow()
        session.add(run)
        session.commit()
    except Exception as e:
        run.status = "failed"
        run.output = str(e)
        run.updated_at = datetime.utcnow()
        session.add(run)
        session.commit()
        yield {"error": str(e)}