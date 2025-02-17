from datetime import datetime, timedelta
from typing import Dict, Any
from app.utils import (
    JST,
    to_utc,
    to_jst,
    DATETIME_FORMAT,
    TIME_FORMAT
)

def get_future_date(days: int = 1) -> str:
    """
    現在時刻からの未来の日付を返す
    
    Args:
        days (int): 何日後の日付を取得するか（デフォルト: 1日後）
    
    Returns:
        str: ISO形式の日付文字列
    """
    future_date = datetime.now(JST) + timedelta(days=days)
    # 時刻を10時に設定（デフォルトの会議開始時刻に合わせる）
    future_date = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    return future_date.strftime(DATETIME_FORMAT)

def get_valid_meeting_data() -> Dict[str, Any]:
    """
    有効な会議データを生成する
    
    Returns:
        Dict[str, Any]: 会議データ
    """
    return {
        "title": "テスト会議",
        "date": get_future_date(),
        "start_time": "10:00",
        "end_time": "11:00",
        "participants": ["田中", "鈴木"],
        "audio_file_path": None,
        "transcript": None,
        "summary": None
    }

def get_valid_task_data() -> Dict[str, Any]:
    """
    有効なタスクデータを生成する
    
    Returns:
        Dict[str, Any]: タスクデータ
    """
    return {
        "content": "テストタスク",
        "assignee": "田中",
        "due_date": get_future_date(2),  # 2日後
        "status": "pending"
    }

# テスト用の定数
MEETING_TITLE = "テスト会議"
TASK_CONTENT = "テストタスク"
VALID_STATUSES = ["pending", "in_progress", "completed"]
PARTICIPANTS = ["田中", "鈴木"]

# 無効なテストデータ生成用の関数（追加）
def get_invalid_meeting_data() -> Dict[str, Dict[str, Any]]:
    """
    各種バリデーションエラーをテストするための無効なデータを生成
    
    Returns:
        Dict[str, Dict[str, Any]]: エラーパターン別の無効なデータ
    """
    base_data = get_valid_meeting_data()
    return {
        "past_date": {
            **base_data,
            "date": (datetime.now(JST) - timedelta(days=1)).strftime(DATETIME_FORMAT)
        },
        "invalid_time_format": {
            **base_data,
            "start_time": "9:5"  # 不正な時刻フォーマット
        },
        "non_10min_interval": {
            **base_data,
            "start_time": "10:05"  # 10分間隔でない時刻
        },
        "end_before_start": {
            **base_data,
            "start_time": "11:00",
            "end_time": "10:00"
        },
        "too_long_duration": {
            **base_data,
            "start_time": "10:00",
            "end_time": "14:00"  # 4時間の会議
        },
        "too_many_participants": {
            **base_data,
            "participants": ["参加者{}".format(i) for i in range(21)]  # 21人の参加者
        }
    }