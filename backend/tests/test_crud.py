from datetime import datetime, timezone, timedelta
from app.crud import (
    create_meeting,
    get_meetings,
    create_task,
    get_tasks_by_meeting,
    update_task
)
from app.schemas import MeetingCreate, TaskCreate
from app.models import Meeting, Task
from app.utils import JST, to_utc
from .test_data import (
    get_valid_meeting_data,
    get_valid_task_data,
    get_invalid_meeting_data,
    VALID_STATUSES
)

def test_create_meeting_crud(db):
    # 有効なデータで会議を作成
    meeting_data = get_valid_meeting_data()
    meeting_schema = MeetingCreate(**meeting_data)
    
    meeting = create_meeting(db, meeting_schema)
    
    assert meeting["title"] == meeting_data["title"]
    assert isinstance(meeting["participants"], list)
    assert meeting["participants"] == meeting_data["participants"]
    assert meeting["start_time"] == meeting_data["start_time"]
    assert meeting["end_time"] == meeting_data["end_time"]

def test_get_meetings_crud(db):
    # 会議を作成
    meeting_data = get_valid_meeting_data()
    meeting_schema = MeetingCreate(**meeting_data)
    create_meeting(db, meeting_schema)
    
    # 会議一覧を取得
    meetings = get_meetings(db, skip=0, limit=10)
    
    assert len(meetings) > 0
    assert isinstance(meetings[0]["participants"], list)
    assert meetings[0]["start_time"] == meeting_data["start_time"]
    assert meetings[0]["end_time"] == meeting_data["end_time"]

def test_create_task_crud(db):
    # 会議を作成
    meeting_data = get_valid_meeting_data()
    meeting_schema = MeetingCreate(**meeting_data)
    meeting = create_meeting(db, meeting_schema)
    
    # タスクを作成
    task_data = get_valid_task_data()
    task_data["meeting_id"] = meeting["id"]
    
    task = create_task(db, task_data)
    
    assert task.content == task_data["content"]
    assert task.meeting_id == meeting["id"]
    assert task.assignee == task_data["assignee"]
    assert task.status == task_data["status"]

def test_get_tasks_by_meeting_crud(db):
    # 会議とタスクを作成
    meeting_data = get_valid_meeting_data()
    meeting_schema = MeetingCreate(**meeting_data)
    meeting = create_meeting(db, meeting_schema)
    
    task_data = get_valid_task_data()
    task_data["meeting_id"] = meeting["id"]
    create_task(db, task_data)
    
    # タスク一覧を取得
    tasks = get_tasks_by_meeting(db, meeting["id"])
    
    assert len(tasks) > 0
    assert tasks[0].meeting_id == meeting["id"]
    assert tasks[0].content == task_data["content"]
    assert tasks[0].assignee == task_data["assignee"]

def test_update_task_crud(db):
    # 会議とタスクを作成
    meeting_data = get_valid_meeting_data()
    meeting_schema = MeetingCreate(**meeting_data)
    meeting = create_meeting(db, meeting_schema)
    
    task_data = get_valid_task_data()
    task_data["meeting_id"] = meeting["id"]
    task = create_task(db, task_data)
    
    # タスクを更新
    update_data = TaskCreate(
        content="更新されたタスク",
        assignee="鈴木",
        due_date=datetime.now(JST) + timedelta(days=3),
        status="completed"
    )
    
    updated_task = update_task(db, task.id, update_data)
    
    assert updated_task.content == "更新されたタスク"
    assert updated_task.assignee == "鈴木"
    assert updated_task.status == "completed"