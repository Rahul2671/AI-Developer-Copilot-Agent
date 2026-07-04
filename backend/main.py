from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.upload import router as upload_router
from api.chat import router as chat_router
from api.project import router as project_router
from api.health import router as health_router
from api.review import router as review_router
from api.plan import router as plan_router

app = FastAPI(
    title="AI Developer Copilot"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    upload_router,
    prefix="/upload",
    tags=["Upload"]
)
app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"]
)
app.include_router(
    project_router,
    prefix="/project",
    tags=["Project"]
)
app.include_router(
    health_router,
    prefix="/health",
    tags=["Health"]
)
app.include_router(
    review_router,
    prefix="/review",
    tags=["Review"]
)
app.include_router(
    plan_router,
    prefix="/plan",
    tags=["Plan"]
)

@app.get("/")
def home():
    return {
        "message":
        "AI Developer Copilot Backend Running"
    }