from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import init_db
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from modules.prompt_lab.router import router as prompt_lab_router
from modules.rag_studio.router import router as rag_studio_router
from modules.agent_builder.router import router as agent_builder_router
from modules.observability.router import router as observability_router
from modules.crew_studio.router import router as crew_studio_router

# Lifespan function to initialize resources when the application starts and clean up when it shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() # Initialize the database when the application starts
    yield

# Create the FastAPI application
app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS configuration to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to match your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Include routers for different modules of the application
app.include_router(prompt_lab_router, prefix="/api/prompt-lab", tags=["Prompt Lab"])
app.include_router(rag_studio_router, prefix="/api/rag-studio", tags=["RAG Studio"])
app.include_router(agent_builder_router, prefix="/api/agent-builder", tags=["Agent Builder"])
app.include_router(crew_studio_router, prefix="/api/crew-studio", tags=["Crew Studio"])
app.include_router(observability_router, prefix="/api/observability", tags=["Observability"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}

