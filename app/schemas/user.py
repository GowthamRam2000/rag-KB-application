from datetime import datetime

from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str
    invite_code: str

class User(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)
class UserDetail(BaseModel):
    id: int
    username: str
    query_count: int
    pdf_upload_count: int
    last_activity_date: datetime

    model_config = ConfigDict(from_attributes=True)