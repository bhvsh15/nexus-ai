from .models import CrewAgent, CrewTask, Crew, CrewRun
from sqlmodel import Session, select
import json
from crewai import Agent, Task, Process, LLM
from crewai import Crew as CrewAICrew
from datetime import datetime

def create_crew_agent(session: Session, name: str, role: str, goal: str, backstory: str, model: str, tools: list[str], description: str | None = None) -> CrewAgent:
    agent = CrewAgent(
        name=name,
        role=role,
        goal=goal,
        backstory=backstory,
        model=model,
        tools=json.dumps(tools),
        description=description
    )
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent

def get_crew_agent(session: Session, agent_id: int) -> CrewAgent | None:
    return session.get(CrewAgent, agent_id)

def get_all_crew_agents(session: Session) -> list[CrewAgent]:
    return session.exec(select(CrewAgent)).all()

def create_task(session: Session, description: str, expected_output: str, agent_id: int) -> CrewTask:
    task = CrewTask(description=description, expected_output=expected_output, agent_id=agent_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_task(session: Session, task_id: int) -> CrewTask | None:
    return session.get(CrewTask, task_id)

def get_all_tasks(session: Session) -> list[CrewTask]:
    return session.exec(select(CrewTask)).all()

def create_crew(session: Session, name: str, process: str, agent_ids: list[int], task_ids: list[int]) -> Crew:
    crew = Crew(
        name=name,
        process=process,
        agent_ids=json.dumps(agent_ids),
        task_ids=json.dumps(task_ids)
    )
    session.add(crew)
    session.commit()
    session.refresh(crew)
    return crew

def get_crew(session: Session, crew_id: int) -> Crew | None:
    return session.get(Crew, crew_id)

def get_all_crews(session: Session) -> list[Crew]:
    return session.exec(select(Crew)).all()

#----------------------------------------------------------
#Creating a crew in Crew AI and running it
#----------------------------------------------------------

def run_crew(session: Session, crew_id: int, input: str) -> CrewRun:
    crew = get_crew(session, crew_id)
    if not crew:
        raise ValueError("Crew not found")
    
    agent_ids = json.loads(crew.agent_ids)
    task_ids = json.loads(crew.task_ids)

    crew_run = CrewRun(crew_id=crew_id, input=input, status="running")
    session.add(crew_run)
    session.commit()
    session.refresh(crew_run)

    try:
        agents = []
        for agent_id in agent_ids:
            agent_data = get_crew_agent(session, agent_id)
            if agent_data:
                llm = LLM(model=f"ollama/{agent_data.model}", base_url="http://localhost:11434")
                agents.append(Agent(
                    role=agent_data.role,
                    goal=agent_data.goal,
                    backstory=agent_data.backstory,
                    llm=llm,
                    verbose=True
                ))

        tasks = []
        for i, task_id in enumerate(task_ids):
            task_data = get_task(session, task_id)
            if task_data:
                tasks.append(Task(
                    description=task_data.description,
                    expected_output=task_data.expected_output,
                    agent=agents[i % len(agents)]
                ))

        process = Process.sequential if crew.process == "sequential" else Process.hierarchical
        crewai_crew = CrewAICrew(agents=agents, tasks=tasks, process=process, verbose=True)
        result = crewai_crew.kickoff()

        crew_run.status = "completed"
        crew_run.output = str(result)

    except Exception as e:
        crew_run.status = "failed"
        crew_run.output = str(e)
    finally:
        crew_run.updated_at = datetime.utcnow()
        session.add(crew_run)
        session.commit()
        session.refresh(crew_run)
    return crew_run