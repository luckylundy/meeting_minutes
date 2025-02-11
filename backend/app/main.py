from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db

# データベースのテーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 新しい会議を作るエンドポイント
@app.post("/meetings/", response_model=schemas.Meeting)
def create_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(get_db)):
    return crud.create_meeting(db=db, meeting=meeting)

# すべての会議を取得するエンドポイント
@app.get("/meetings/", response_model=list[schemas.Meeting])
def read_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meetings = crud.get_meetings(db, skip=skip, limit=limit)
    return meetings

# 特定のIDの会議を取得するエンドポイント
@app.get("/meetings/{meeting_id}", response_model=schemas.Meeting)
def read_meeting(meeting_id: int, db: Session = Depends(get_db)):
    db_meeting = crud.get_meeting_by_id(db, meeting_id=meeting_id)
    if db_meeting is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    return db_meeting

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