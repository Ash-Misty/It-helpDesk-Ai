from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.queries import router as queries_router
from app.api.classification import router as classification_router
from app.api.tickets import router as tickets_router
from app.api.agent import router as agent_router
from app.api.state import router as state_router
from app.api.memory import router as memory_router
from app.api.knowledge import router as knowledge_router
from app.api.rag import router as rag_router
from app.api.troubleshooting import router as troubleshooting_router

app = FastAPI(
    title="AI IT Helpdesk Agent",
    description="Backend API for the AI IT Helpdesk application.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(queries_router, prefix="/api", tags=["queries"])
app.include_router(classification_router, prefix="/api", tags=["classification"])
app.include_router(tickets_router, prefix="/api", tags=["tickets"])
app.include_router(agent_router, prefix="/api", tags=["agent"])
app.include_router(state_router, prefix="/api", tags=["state"])
app.include_router(memory_router, prefix="/api", tags=["memory"])
app.include_router(knowledge_router, prefix="/api", tags=["knowledge"])
app.include_router(rag_router, prefix="/api", tags=["rag"])
app.include_router(troubleshooting_router, prefix="/api", tags=["troubleshooting"])
