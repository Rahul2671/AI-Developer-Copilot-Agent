from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload import router as upload_router
from api.chat import router as chat_router


app = FastAPI(
    title="AI Developer Copilot"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
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



@app.get("/")
def home():

    return {
        "message":
        "AI Developer Copilot Backend Running"
    }