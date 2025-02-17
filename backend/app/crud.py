from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db
from .models import Meeting as MeetingModel
from .schemas import MeetingCreate
from datetime import datetime, timezone
from json import dumps, loads

def create_meeting(db: Session, meeting: schemas.MeetingCreate):
    try:
        # モデルのコンストラクタでJSON変換を行うように変更したので、
        # 直接participantsを渡せる
        db_meeting = models.Meeting(
            title=meeting.title,
            date=meeting.date.replace(tzinfo=timezone.utc),
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            participants=meeting.participants,  # 直接リストを渡す
            audio_file_path=meeting.audio_file_path,
            transcript=meeting.transcript,
            summary=meeting.summary
        )
        
        db.add(db_meeting)
        db.commit()
        db.refresh(db_meeting)
        
        # モデルが自動的にJSONを処理するので、
        # participants_listプロパティを使用
        return {
            "id": db_meeting.id,
            "title": db_meeting.title,
            "date": db_meeting.date,
            "start_time": db_meeting.start_time,
            "end_time": db_meeting.end_time,
            "participants": db_meeting.participants_list,
            "audio_file_path": db_meeting.audio_file_path,
            "transcript": db_meeting.transcript,
            "summary": db_meeting.summary,
            "created_at": db_meeting.created_at,
            "updated_at": db_meeting.updated_at,
            "tasks": []
        }
    except Exception as e:
        db.rollback()
        raise

def get_meetings(db: Session, skip: int = 0, limit: int = 100):
    meetings = db.query(models.Meeting).offset(skip).limit(limit).all()
    return [
        {
            "id": meeting.id,
            "title": meeting.title,
            "date": meeting.date,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
            "participants": meeting.participants_list,  # プロパティを使用
            "audio_file_path": meeting.audio_file_path,
            "transcript": meeting.transcript,
            "summary": meeting.summary,
            "created_at": meeting.created_at,
            "updated_at": meeting.updated_at
        }
        for meeting in meetings
    ]

def get_meeting_by_id(db: Session, meeting_id: int):
    try:
        meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        return meeting  # モデルが自動的にJSONを処理
    except Exception as e:
        print(f"Error in get_meeting_by_id: {str(e)}")
        return None

def update_meeting(db: Session, meeting_id: int, meeting: schemas.MeetingCreate):
    try:
        db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if db_meeting is None:
            return None
        
        # データを更新（participantsは特別扱い）
        meeting_data = meeting.model_dump()
        participants = meeting_data.pop('participants', [])  # participantsを取り出す
        
        # その他のフィールドを更新
        for key, value in meeting_data.items():
            setattr(db_meeting, key, value)
        
        # participantsを適切に変換して設定
        db_meeting.participants = dumps(participants)
        
        db.commit()
        db.refresh(db_meeting)
        return {
            "id": db_meeting.id,
            "title": db_meeting.title,
            "date": db_meeting.date,
            "start_time": db_meeting.start_time,
            "end_time": db_meeting.end_time,
            "participants": db_meeting.participants_list,  # リストとして取得
            "audio_file_path": db_meeting.audio_file_path,
            "transcript": db_meeting.transcript,
            "summary": db_meeting.summary,
            "created_at": db_meeting.created_at,
            "updated_at": db_meeting.updated_at,
            "tasks": []
        }
    except Exception as e:
        db.rollback()
        raise

def delete_meeting(db: Session, meeting_id: int):
    try:
        db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if db_meeting is None:
            return None
        
        db.delete(db_meeting)
        db.commit()
        return db_meeting
    except Exception as e:
        db.rollback()
        raise



# タスクを新規作成する関数
def create_task(db: Session, task_data: dict):
    try:
        # TaskCreateモデルでバリデーション
        task_create = schemas.TaskCreate(
            content=task_data["content"],
            assignee=task_data.get("assignee"),
            due_date=task_data.get("due_date"),
            status=task_data.get("status", "pending")
        )
        
        db_task = models.Task(
            meeting_id=task_data["meeting_id"],
            content=task_create.content,
            assignee=task_create.assignee,
            due_date=task_create.due_date,
            status=task_create.status
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise

# 特定の会議のタスク一覧取得
def get_tasks_by_meeting(db: Session, meeting_id: int):
    try:
        # 会議の存在確認
        meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if not meeting:
            return []

        # タスクの取得
        tasks = db.query(models.Task).filter(models.Task.meeting_id == meeting_id).all()
        return tasks
    except Exception as e:
        print(f"Error getting tasks: {str(e)}")
        return []

# タスクの更新
def update_task(db: Session, task_id: int, task: schemas.TaskCreate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        for key, value in task.model_dump().items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

# タスクの削除
def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task