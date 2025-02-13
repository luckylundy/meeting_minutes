from pydantic import BaseModel, Field, field_validator
from datetime import datetime, time
from typing import Optional, List
from .exceptions import (
    DateValidationError, 
    ContentLengthError,
    ValidationError
)
import re

class TaskBase(BaseModel):
    # Fieldを使用してより詳細なバリデーションを追加
    content: str = Field(
        ...,  # 必須項目
        max_length=1000,
        description="タスクの内容"
    )
    assignee: Optional[str] = Field(
        None,
        pattern="^[a-zA-Z0-9_-]+$",
        description="担当者のユーザーID"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="タスクの期限"
    )
    status: str = Field(
        "pending",
        description="タスクの状態"
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if len(v) > 1000:
            raise ContentLengthError(max_length=1000)
        return v

    @field_validator('assignee')
    @classmethod
    def validate_assignee(cls, v):
        if v is not None:
            if not re.match("^[a-zA-Z0-9_-]+$", v):
                raise ValidationError("担当者IDは英数字、アンダースコア、ハイフンのみ使用可能です")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_status = ['pending', 'in_progress', 'completed']
        if v not in allowed_status:
            raise ValidationError(f"ステータスは {', '.join(allowed_status)} のいずれかにしてください")
        return v

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v and v < datetime.now():
            raise DateValidationError()
        return v

class MeetingBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="会議のタイトル"
    )
    date: datetime = Field(..., description="会議の日付")
    start_time: str = Field(..., description="開始時刻（HH:MM形式）")
    end_time: str = Field(..., description="終了時刻（HH:MM形式）")
    participants: Optional[List[str]] = Field(
        default=[],
        description="参加者リスト"
    )
    audio_file_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None

    @field_validator('date')
    @classmethod
    def validate_meeting_date(cls, v):
        if v < datetime.now():
            raise DateValidationError()
        return v

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v):
        try:
            hour, minute = map(int, v.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
            time(hour, minute)
        except:
            raise ValidationError("時刻は HH:MM 形式で入力してください（例: 09:30）")
        return v

    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, values, field):
        start = values.get('start_time')
        end = field
        if start and end:
            if start >= end:
                raise ValidationError("終了時刻は開始時刻より後にしてください")
        return end

class TaskCreate(TaskBase):
    pass    # TaskBaseを継承するだけで、meeting_idは不要

class Task(TaskBase):
    id: int
    meeting_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    date: datetime
    start_time: str
    end_time: str
    participants: Optional[List[str]] = []
    audio_file_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None

    @field_validator('date')
    @classmethod
    def validate_meeting_date(cls, v):
        if v < datetime.now():
            raise DateValidationError()
        return v

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v):
        try:
            hour, minute = map(int, v.split(':'))
            time(hour, minute)
        except:
            raise ValidationError("時刻は HH:MM 形式で入力してください（例: 09:30）")
        return v

    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, values, field):
        start = values.get('start_time')
        end = field
        if start and end:
            if start >= end:
                raise ValidationError("終了時刻は開始時刻より後にしてください")
        return end

class MeetingCreate(MeetingBase):
    pass  # MeetingBaseを継承

class Meeting(MeetingBase):
    id: int
    date: datetime
    created_at: datetime
    updated_at: datetime
    tasks: List[Task] = []

    class Config:
        from_attributes = True