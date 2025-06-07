import os
from dotenv import load_dotenv
from dotenv import find_dotenv
load_dotenv(find_dotenv())
PROJECT_NAME: str = "RAG Application API"
API_V1_STR: str = "/api/v1"
DATABASE_USER: str = os.getenv("DATABASE_USER")
DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME: str = os.getenv("DATABASE_NAME")
INSTANCE_CONNECTION_NAME: str = os.getenv("INSTANCE_CONNECTION_NAME")
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE_NAME}"

SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_bad_default_secret_key")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30