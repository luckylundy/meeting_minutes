from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, event
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base
from json import loads, dumps

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    participants = Column(Text, nullable=True)
    audio_file_path = Column(String(255), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # リレーションシップ
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")

    @property
    def participants_list(self):
        """participantsをJSON文字列からリストに変換して返す"""
        if self.participants:
            try:
                return loads(self.participants)
            except:
                return []
        return []

    def __init__(self, **kwargs):
        """初期化時にparticipantsをJSON文字列に変換"""
        if 'participants' in kwargs and isinstance(kwargs['participants'], list):
            kwargs['participants'] = dumps(kwargs['participants'])
        super().__init__(**kwargs)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    content = Column(Text, nullable=False)
    assignee = Column(String(100))
    due_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    meeting = relationship("Meeting", back_populates="tasks")


# SQLAlchemyイベントリスナー
@event.listens_for(Meeting, 'before_update')
def convert_participants_to_json(mapper, connection, target):
    """更新時にparticipantsをJSON文字列に変換"""
    if hasattr(target, 'participants') and isinstance(target.participants, list):
        target.participants = dumps(target.participants)

@event.listens_for(Meeting, 'load')
def convert_participants_from_json(target, context):
    """データベースからロード時にparticipantsをリストに変換"""
    if target.participants:
        try:
            target.participants = loads(target.participants)
        except:
            target.participants = []