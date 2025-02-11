from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TaskBase(BaseModel):
    content: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "pending"

class TaskCreate(TaskBase):
    meeting_id: int

class Task(TaskBase):
    id: int
    meeting_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MeetingBase(BaseModel):
    title: str
    date: datetime
    start_time: str
    end_time: str
    participants: Optional[List[str]] = []
    audio_file_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None

class MeetingCreate(MeetingBase):
    pass  # MeetingBaseを継承

class Meeting(MeetingBase):
    id: int
    date: datetime
    created_at: datetime
    updated_at: datetime
    tasks: List[Task] = []

    class Config:
        orm_mode = True