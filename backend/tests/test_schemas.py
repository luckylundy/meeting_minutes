from datetime import datetime, timedelta
import pytest
from app.schemas import MeetingCreate, TaskCreate
from pydantic import ValidationError as PydanticValidationError
from app.exceptions import ValidationError as AppValidationError


def test_meeting_create_validation():
    # 正常なケース
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
    
    meeting_data = {
        "title": "テスト会議",
        "date": future_date,  # 動的に生成した未来の日付を使用
        "start_time": "10:00",
        "end_time": "11:00",
        "participants": ["田中", "鈴木"],
        "audio_file_path": None,
        "transcript": None,
        "summary": None
    }
    meeting = MeetingCreate(**meeting_data)
    assert meeting.title == meeting_data["title"]

    # エラーケース（タイトルが長すぎる）
    with pytest.raises(PydanticValidationError):
        MeetingCreate(
            title="あ" * 101,  # 100文字制限を超える
            date="2028-02-16T10:00:00",
            start_time="10:00",
            end_time="11:00",
            participants=[]
        )

def test_task_create_validation():
    # 正常なケース
    # 現在時刻から1年後の日付を作成
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
    
    task_data = {
        "content": "テストタスク",
        "assignee": "田中",
        "due_date": future_date,  # 動的に生成した未来の日付を使用
        "status": "pending"
    }
    task = TaskCreate(**task_data)
    assert task.content == task_data["content"]

    # エラーケース（不正なステータス）
with pytest.raises(AppValidationError):  
        TaskCreate(
            content="テストタスク",
            assignee="田中",
            due_date="2028-02-15T10:00:00",
            status="invalid_status"  # 許可されていないステータス
        )