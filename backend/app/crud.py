from sqlalchemy.orm import Session
from . import models, schemas
from json import dumps, loads

# 会議を新規作成する関数
def create_meeting(db: Session, meeting: schemas.MeetingCreate):

    # participantsをJSON文字列に変換
    participants_json = dumps(meeting.participants) if meeting.participants else "[]"

    # 新しい会議の設計図
    db_meeting = models.Meeting(
        title=meeting.title,
        date=meeting.date,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        participants=participants_json, # JSON文字列として保存
        audio_file_path=meeting.audio_file_path,
        transcript=meeting.transcript,
        summary=meeting.summary
    )
    
    # データベースに会議を追加
    db.add(db_meeting)
    db.commit()  # 変更を確定
    db.refresh(db_meeting)  # 最新の情報を取得
    
    # 保存したデータを取得する前に、participantsをJSON文字列からリストに戻す
    setattr(db_meeting, 'participants', loads(db_meeting.participants))
    return db_meeting

# すべての会議を取得する関数
def get_meetings(db: Session, skip: int = 0, limit: int = 100):
    meetings = db.query(models.Meeting).offset(skip).limit(limit).all()
    # 各meetingのparticipantsをJSON文字列からリストに変換
    for meeting in meetings:
        meeting.participants = loads(meeting.participants)
    return meetings

# 特定のIDの会議を取得する関数
def get_meeting_by_id(db: Session, meeting_id: int):
    return db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()

# 会議を更新する関数
def update_meeting(db: Session, meeting_id: int, meeting: schemas.MeetingCreate):
    # データベースから会議を探す
    db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    
    if db_meeting is None:
        return None
    
    # 新しい情報で上書き
    for key, value in meeting.model_dump(exclude_unset=True).items():
        setattr(db_meeting, key, value)
    
    db.commit()
    db.refresh(db_meeting)
    
    return db_meeting

# 会議を削除する関数
def delete_meeting(db: Session, meeting_id: int):
    # データベースから会議を探す
    db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    
    if db_meeting is None:
        return None
    
    # 会議を削除
    db.delete(db_meeting)
    db.commit()
    
    return db_meeting