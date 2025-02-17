from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError
from . import crud, models, schemas
from .database import engine, get_db
from .error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from .exceptions import BaseAppException, ResourceNotFound
from pydantic import BaseModel, Field
from .schemas import MeetingCreate, Meeting
from .crud import create_meeting
import logging

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# データベースのテーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="会議議事録自動生成アプリ",
    description="会議の記録と議事録を自動で生成するためのAPI",
    version="1.0.0"
)

# グローバルな例外ハンドラーの登録
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(PydanticValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# 新しい会議を作るエンドポイント
@app.post("/api/meetings", response_model=schemas.Meeting)
def create_meeting_endpoint(
    meeting: schemas.MeetingCreate, 
    db: Session = Depends(get_db)
):
    """
    新しい会議を作成します。
    
    - **title**: 会議のタイトル
    - **date**: 会議の日付（例：2025-03-01T10:00:00）
    - **start_time**: 開始時刻（例：10:00）
    - **end_time**: 終了時刻（例：11:00）
    - **participants**: 参加者のリスト
    """

    try:
        return crud.create_meeting(db=db, meeting=meeting)
    except BaseAppException as e:
        raise e
    except Exception as e:
        raise BaseAppException(
            message="会議の作成中にエラーが発生しました",
            status_code=500
        )

# すべての会議を取得するエンドポイント
@app.get("/api/meetings/", response_model=list[schemas.Meeting])
def read_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    登録されているすべての会議の一覧を取得します。
    
    - **skip**: スキップする会議の数（ページネーション用、デフォルト：0）
    - **limit**: 取得する会議の最大数（ページネーション用、デフォルト：100）
    
    返却値：会議のリスト
    """
    meetings = crud.get_meetings(db, skip=skip, limit=limit)
    return meetings

# 特定のIDの会議を取得するエンドポイント
@app.get("/api/meetings/{meeting_id}", response_model=schemas.Meeting)
def read_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """
    指定されたIDの会議の詳細情報を取得します。
    
    - **meeting_id**: 取得したい会議のID
    
    返却値：指定されたIDの会議の詳細情報
    """
    meeting = crud.get_meeting_by_id(db, meeting_id=meeting_id)
    if meeting is None:
        raise ResourceNotFound("会議")
    return meeting

# 会議を更新するエンドポイント
@app.put("/api/meetings/{meeting_id}", response_model=schemas.Meeting)
def update_meeting(meeting_id: int, meeting: schemas.MeetingCreate, db: Session = Depends(get_db)):
    """
    指定されたIDの会議の情報を更新します。
    
    - **meeting_id**: 更新したい会議のID
    - **title**: 会議の新しいタイトル
    - **date**: 会議の新しい日付（例：2025-03-01T10:00:00）
    - **start_time**: 新しい開始時刻（例：10:00）
    - **end_time**: 新しい終了時刻（例：11:00）
    - **participants**: 新しい参加者のリスト
    
    返却値：更新された会議の情報
    """
    updated_meeting = crud.update_meeting(db, meeting_id=meeting_id, meeting=meeting)
    if updated_meeting is None:
        raise ResourceNotFound("会議")
    return updated_meeting

# 会議を削除するエンドポイント
@app.delete("/api/meetings/{meeting_id}", response_model=schemas.Meeting)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """
    指定されたIDの会議を削除します。
    
    - **meeting_id**: 削除したい会議のID
    
    返却値：削除された会議の情報
    """
    deleted_meeting = crud.delete_meeting(db, meeting_id=meeting_id)
    if deleted_meeting is None:
        raise ResourceNotFound("会議")
    return deleted_meeting



# タスク作成
@app.post("/api/meetings/{meeting_id}/tasks/", response_model=schemas.Task)
def create_meeting_task(meeting_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    指定された会議に新しいタスクを作成します。
    
    - **meeting_id**: タスクを追加したい会議のID
    - **content**: タスクの内容（1000文字以内）
    - **assignee**: タスクの担当者（オプション）
    - **due_date**: タスクの期限（オプション）
    - **status**: タスクの状態（pending/in_progress/completed）
    
    返却値：作成されたタスクの情報
    """
    # 会議の存在確認
    meeting = crud.get_meeting_by_id(db, meeting_id)
    if meeting is None:
        raise ResourceNotFound("会議")
    
    # タスク作成用のデータを準備
    task_data = task.model_dump()
    task_data["meeting_id"] = meeting_id
    
    return crud.create_task(db=db, task_data=task_data)

# 会議のタスク一覧取得
@app.get("/api/meetings/{meeting_id}/tasks/", response_model=list[schemas.Task])
def read_meeting_tasks(meeting_id: int, db: Session = Depends(get_db)):
    """
    指定された会議のタスク一覧を取得します。
    
    - **meeting_id**: タスク一覧を取得したい会議のID
    
    返却値：指定された会議のタスク一覧
    """
    tasks = crud.get_tasks_by_meeting(db, meeting_id)
    return tasks

# タスク更新
@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    指定されたIDのタスクを更新します。
    
    - **task_id**: 更新したいタスクのID
    - **content**: タスクの新しい内容（1000文字以内）
    - **assignee**: タスクの新しい担当者（オプション）
    - **due_date**: タスクの新しい期限（オプション）
    - **status**: タスクの新しい状態（pending/in_progress/completed）
    
    返却値：更新されたタスクの情報
    """
    updated_task = crud.update_task(db, task_id=task_id, task=task)
    if updated_task is None:
        raise ResourceNotFound("タスク")
    return updated_task

# タスク削除
@app.delete("/api/tasks/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    指定されたIDのタスクを削除します。
    
    - **task_id**: 削除したいタスクのID
    
    返却値：削除されたタスクの情報
    """
    deleted_task = crud.delete_task(db, task_id=task_id)
    if deleted_task is None:
        raise ResourceNotFound("タスク")
    return deleted_task
