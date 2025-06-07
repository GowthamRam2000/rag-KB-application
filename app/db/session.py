# app/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector

from app.core.config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME, INSTANCE_CONNECTION_NAME

# This function determines if we are running in the Cloud Run environment
def is_production():
    return os.environ.get("K_SERVICE") is not None

def get_conn():
    # This is the new, production-ready way to connect
    with Connector() as connector:
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME, # e.g. "project:region:instance"
            "pg8000",
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            db=DATABASE_NAME,
        )
        return conn

# Use the appropriate connection method based on the environment
if is_production():
    # In production (Cloud Run), use the Cloud SQL Connector
    engine = create_engine("postgresql+pg8000://", creator=get_conn)
else:
    # For local development, use the Cloud SQL Auth Proxy connection string
    DB_HOST = "127.0.0.1"
    DB_PORT = "5432"
    DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE_NAME}"
    engine = create_engine(DATABASE_URL)

# The rest of the file is the same
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)