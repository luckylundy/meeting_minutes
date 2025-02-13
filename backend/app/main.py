from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db
from fastapi import FastAPI
from .error_handlers import app_exception_handler
from .exceptions import BaseAppException, ResourceNotFound

# データベースのテーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# グローバルな例外ハンドラーの登録
app.add_exception_handler(BaseAppException, app_exception_handler)

# 新しい会議を作るエンドポイント
@app.post("/meetings/", response_model=schemas.Meeting)
def create_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_meeting(db=db, meeting=meeting)
    except BaseAppException as e:
        # 自作の例外は、そのままエラーハンドラーに渡す
        raise e
    except Exception as e:
        # 予期せぬエラーは一般的なエラーメッセージに変換
        raise BaseAppException(
            message="会議の作成中にエラーが発生しました",
            status_code=500
        )

# すべての会議を取得するエンドポイント
@app.get("/meetings/", response_model=list[schemas.Meeting])
def read_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meetings = crud.get_meetings(db, skip=skip, limit=limit)
    return meetings

# 特定のIDの会議を取得するエンドポイント
@app.get("/meetings/{meeting_id}", response_model=schemas.Meeting)
def read_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = crud.get_meeting_by_id(db, meeting_id=meeting_id)
    if meeting is None:
        raise ResourceNotFound("会議")
    return meeting

# 会議を更新するエンドポイント
@app.put("/meetings/{meeting_id}", response_model=schemas.Meeting)
def update_meeting(meeting_id: int, meeting: schemas.MeetingCreate, db: Session = Depends(get_db)):
    updated_meeting = crud.update_meeting(db, meeting_id=meeting_id, meeting=meeting)
    if updated_meeting is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    return updated_meeting

# 会議を削除するエンドポイント
@app.delete("/meetings/{meeting_id}", response_model=schemas.Meeting)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    deleted_meeting = crud.delete_meeting(db, meeting_id=meeting_id)
    if deleted_meeting is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    return deleted_meeting



# タスク作成
@app.post("/meetings/{meeting_id}/tasks/", response_model=schemas.Task)
def create_meeting_task(meeting_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # 会議の存在確認
    meeting = crud.get_meeting_by_id(db, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    
    # タスク作成用のデータを準備
    task_data = task.model_dump()
    task_data["meeting_id"] = meeting_id
    
    return crud.create_task(db=db, task_data=task_data)

# 会議のタスク一覧取得
@app.get("/meetings/{meeting_id}/tasks/", response_model=list[schemas.Task])
def read_meeting_tasks(meeting_id: int, db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_meeting(db, meeting_id)
    return tasks

# タスク更新
@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    updated_task = crud.update_task(db, task_id=task_id, task=task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")
    return updated_task

# タスク削除
@app.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted_task = crud.delete_task(db, task_id=task_id)
    if deleted_task is None:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")
    return deleted_task