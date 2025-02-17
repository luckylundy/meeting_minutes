from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Dict
import json
import re

# 定数定義
JST = timezone(timedelta(hours=9))
UTC = timezone.utc
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MAX_MEETING_HOURS = 3
MEETING_INTERVAL_MINUTES = 10

# タイムゾーン変換関数
def to_jst(dt: datetime) -> datetime:
    """UTC→JSTの変換"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(JST)

def to_utc(dt: datetime) -> datetime:
    """JST→UTCの変換"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=JST)
    return dt.astimezone(UTC)

# 時刻検証関数
def validate_time_format(time_str: str) -> bool:
    """HH:MM形式の時刻文字列を検証"""
    pattern = r'^([0-1][0-9]|2[0-3]):([0-5][0-9])$'
    if not re.match(pattern, time_str):
        return False
    return True

def validate_time_interval(time_str: str) -> bool:
    """10分間隔の時刻かどうかを検証"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return minute % MEETING_INTERVAL_MINUTES == 0
    except ValueError:
        return False

def validate_meeting_duration(start_time: str, end_time: str) -> bool:
    """会議時間が3時間以内かを検証"""
    start = datetime.strptime(start_time, TIME_FORMAT)
    end = datetime.strptime(end_time, TIME_FORMAT)
    duration = end - start
    return duration <= timedelta(hours=MAX_MEETING_HOURS)

# JSON変換用のカスタムエンコーダー
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            # JSTに変換してフォーマット
            jst_time = to_jst(obj)
            return jst_time.strftime(DATETIME_FORMAT)
        return super().default(obj)

# JSON変換関数
def datetime_to_json(dt: datetime) -> str:
    """datetime型をJST形式のJSON文字列に変換"""
    return json.dumps(dt, cls=CustomJSONEncoder)

def json_to_datetime(dt_str: str) -> datetime:
    """JSON文字列をdatetime型に変換"""
    dt = datetime.strptime(dt_str, DATETIME_FORMAT)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=JST)
    return to_utc(dt)

def serialize_participants(participants: list) -> str:
    """参加者リストをJSON文字列に変換"""
    return json.dumps(participants, ensure_ascii=False)

def deserialize_participants(participants_json: Optional[str]) -> list:
    """JSON文字列を参加者リストに変換"""
    if not participants_json:
        return []
    try:
        return json.loads(participants_json)
    except json.JSONDecodeError:
        return []

# エラーメッセージ生成
def format_validation_error(message: str) -> Dict[str, Any]:
    """バリデーションエラーメッセージの整形"""
    return {
        "error": "バリデーションエラー",
        "message": message,
        "timestamp": datetime.now(JST).strftime(DATETIME_FORMAT)
    }