from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field
from .exceptions import DateValidationError, ValidationError, ContentLengthError
from .utils import (
    validate_time_format,
    validate_time_interval,
    validate_meeting_duration,
    to_utc,
    to_jst,
    JST,
    format_validation_error
)
import re


class TaskBase(BaseModel):
    content: str = Field(
        ...,
        max_length=1000,
        description="タスクの内容"
    )
    assignee: Optional[str] = Field(
        None,
        pattern=r"^[\w\-\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF]+$",
        max_length=30,  # 追加：参加者名の最大文字数
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

    # 既存のバリデーター
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
            if not re.match(r"^[\w\-\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF]+$", v):
                raise ValidationError("担当者IDは英数字・アンダースコア・ハイフン・ひらがな・カタカナ・漢字のみ使用可能です")
            if len(v) > 30:
                raise ValidationError("担当者名は30文字以内で入力してください")
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
        if v is not None:
            try:
                now = datetime.now(JST)
                v = to_utc(v)  # UTCに変換
                if v < now:
                    raise DateValidationError()
                return v
            except DateValidationError:
                raise
            except Exception as e:
                raise ValidationError(f"無効な日付形式です: {str(e)}")
        return v


class MeetingBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemyモデルとの互換性を維持
        json_encoders={list: lambda v: v}  # リストの変換を追加
    )
    
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

    # 日付バリデーター（修正）
    @field_validator('date')
    @classmethod
    def validate_meeting_date(cls, v): 
        try:
            now = datetime.now(JST)
            v = to_utc(v)  # UTCに変換
            if v < now:
                raise DateValidationError()
            return v
        except DateValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"無効な日付形式です: {str(e)}")

    # 時刻フォーマットバリデーター（修正）
    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v):
        if not validate_time_format(v):
            raise ValidationError("時刻は HH:MM 形式で入力してください（例: 09:30）")
        if not validate_time_interval(v):
            raise ValidationError("時刻は10分単位で指定してください")
        return v

    # 終了時刻バリデーター（修正）
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v: str, info):
        try:
            start_time = info.data.get('start_time')
            if start_time and v:
                if start_time >= v:
                    raise ValidationError("終了時刻は開始時刻より後にしてください")
                if not validate_meeting_duration(start_time, v):
                    raise ValidationError("会議時間は3時間以内にしてください")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError("時刻の検証中にエラーが発生しました")
        return v

    # 参加者リストバリデーター（新規追加）
    @field_validator('participants')
    @classmethod
    def validate_participants_length(cls, v):
        if len(v) > 20:
            raise ValidationError("参加者は20名以内にしてください")
        if not v:
            return []
        for participant in v:
            if len(participant) > 30:
                raise ValidationError("参加者名は30文字以内で入力してください")
            if not re.match(r"^[\w\-\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF]+$", participant):
                raise ValidationError("参加者名は英数字・アンダースコア・ハイフン・ひらがな・カタカナ・漢字のみ使用可能です")
        return v

class TaskCreate(TaskBase):
    pass    # TaskBaseを継承するだけで、meeting_idは不要

class Task(TaskBase):
    id: int
    meeting_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class MeetingCreate(MeetingBase):
    pass  # MeetingBaseを継承

class Meeting(MeetingBase):
    id: int
    date: datetime
    created_at: datetime
    updated_at: datetime
    tasks: List[Task] = []

    model_config = ConfigDict(from_attributes=True)