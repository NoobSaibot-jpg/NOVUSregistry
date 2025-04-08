from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String)
    category = Column(String)
    project_type = Column(String)
    stage = Column(String)
    project_code_full = Column(String)
    project_code_short = Column(String)
    project_name = Column(String)
    sheet_number = Column(String)
    is_separate_doc = Column(Integer)
    box_number = Column(String)
    folder_number = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProjectCreate(BaseModel):
    file_name: str
    category: str
    project_type: str
    stage: str
    project_code_full: str
    project_code_short: str
    project_name: str
    sheet_number: str
    is_separate_doc: int
    box_number: str
    folder_number: str
    file_path: str

class ProjectResponse(ProjectCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 