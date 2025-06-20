

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import endpoints
from app.core.config import PROJECT_NAME, API_V1_STR
from app.db.base import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)
app = FastAPI(title=PROJECT_NAME)
origins = [
    "http://localhost:5173",
    "http://localhost:5174",

]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix=API_V1_STR)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {PROJECT_NAME}"}
