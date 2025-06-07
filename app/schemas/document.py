
from pydantic import BaseModel, ConfigDict

class Document(BaseModel):
    id: int
    filename: str

    model_config = ConfigDict(from_attributes=True)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    source_documents: list[str]