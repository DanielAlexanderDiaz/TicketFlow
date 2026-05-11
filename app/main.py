from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import init_db
from app.api.routers.auth_router import router as auth_router
from app.api.routers.usuario_router import router as usuario_router
from app.api.routers.ticket_router import router as ticket_router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    
app = FastAPI(
    title="TicketFlow",
    description="TicketFlow API",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(usuario_router, prefix="/api/v1")
app.include_router(ticket_router, prefix="/api/v1")