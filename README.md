# Full-Stack RAG Application

This is a complete Retrieval-Augmented Generation (RAG) web application built with a Python (FastAPI) backend and a Vue.js frontend, deployed on Google Cloud.

## Features

- Secure user registration with invite codes and JWT authentication.
- Upload PDF and DOCX documents for knowledge base creation.
- Ask questions in a modern chat interface and receive AI-generated answers based on the documents.
- Persistent daily rate-limiting for queries and uploads.
- Cloud-native architecture using Google Cloud Run, Cloud SQL, and Cloud Storage.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Gunicorn
- **Frontend:** Vue.js, Vuetify, Pinia, Axios
- **Database:** PostgreSQL (on Google Cloud SQL)
- **AI/ML:** Google Gemini Models via Vertex AI
- **Deployment:** Docker, Google Cloud Run, Artifact Registry

## Setup & Installation

1.  Clone the repository.
2.  Set up the backend environment variables in a `.env` file (see `.env.example`).
3.  Install Python dependencies: `pip install -r requirements.txt`
4.  Run the backend server: `uvicorn app.main:app --reload`