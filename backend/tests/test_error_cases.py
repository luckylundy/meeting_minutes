import pytest
from fastapi.testclient import TestClient
from app.utils import JST
from .test_data import (
    get_valid_meeting_data,
    get_valid_task_data,
    get_invalid_meeting_data,
    VALID_STATUSES
)

def test_meeting_not_found(client):
    """存在しない会議のテスト"""
    response = client.get("/api/meetings/999")
    assert response.status_code == 404
    assert "会議が見つかりません" in response.json()["detail"]

def test_invalid_meeting_data(client):
    """無効な会議データのテスト"""
    # タイトルが空のケース
    invalid_data = get_valid_meeting_data()
    invalid_data["title"] = ""
    response = client.post("/api/meetings", json=invalid_data)
    assert response.status_code == 422

def test_delete_nonexistent_meeting(client):
    """存在しない会議の削除テスト"""
    response = client.delete("/api/meetings/999")
    assert response.status_code == 404
    assert "会議が見つかりません" in response.json()["detail"]

def test_invalid_task_status(client):
    """無効なタスクステータスのテスト"""
    # まず会議を作成
    meeting_data = get_valid_meeting_data()
    create_response = client.post("/api/meetings", json=meeting_data)
    meeting_id = create_response.json()["id"]

    # 不正なステータスでタスクを作成
    task_data = get_valid_task_data()
    task_data["status"] = "invalid_status"
    response = client.post(f"/api/meetings/{meeting_id}/tasks/", json=task_data)
    assert response.status_code == 422
    assert "ステータス" in response.json()["detail"]

def test_past_meeting_date(client):
    """過去の日付での会議作成テスト"""
    invalid_data = get_invalid_meeting_data()["past_date"]
    response = client.post("/api/meetings", json=invalid_data)
    assert response.status_code == 422
    assert "過去の日付" in response.json()["detail"]

def test_too_many_participants(client):
    """参加者数超過のテスト"""
    invalid_data = get_invalid_meeting_data()["too_many_participants"]
    response = client.post("/api/meetings", json=invalid_data)

    # デバッグ情報を出力
    print("Response status code:", response.status_code)
    print("Response JSON:", response.json())

    assert response.status_code == 422
    assert "参加者は20名以内にしてください" in response.json()["detail"]

def test_invalid_participant_name(client):
    """無効な参加者名のテスト"""
    meeting_data = get_valid_meeting_data()
    meeting_data["participants"] = ["@無効な名前#"]
    response = client.post("/api/meetings", json=meeting_data)
    assert response.status_code == 422
    assert "参加者名" in response.json()["detail"]

def test_long_participant_name(client):
    """参加者名が長すぎる場合のテスト"""
    meeting_data = get_valid_meeting_data()
    meeting_data["participants"] = ["あ" * 31]  # 31文字の名前
    response = client.post("/api/meetings", json=meeting_data)
    assert response.status_code == 422
    assert "30文字以内" in response.json()["detail"]

def test_create_task_for_nonexistent_meeting(client):
    """存在しない会議へのタスク作成テスト"""
    task_data = get_valid_task_data()
    response = client.post("/api/meetings/999/tasks/", json=task_data)
    assert response.status_code == 404
    assert "会議が見つかりません" in response.json()["detail"]

def test_invalid_meeting_time_format(client):
    """無効な会議時刻フォーマットのテスト"""
    # 不正な時刻フォーマット
    invalid_data = get_invalid_meeting_data()["invalid_time_format"]
    response = client.post("/api/meetings", json=invalid_data)
    assert response.status_code == 422
    assert "HH:MM 形式" in response.json()["detail"]

def test_non_10min_interval_meeting(client):
    """10分間隔でない会議時刻のテスト"""
    invalid_data = get_invalid_meeting_data()["non_10min_interval"]
    response = client.post("/api/meetings", json=invalid_data)
    assert response.status_code == 422
    assert "10分単位" in response.json()["detail"]

def test_meeting_too_long(client):
    """会議時間が長すぎる場合のテスト"""
    invalid_data = get_invalid_meeting_data()["too_long_duration"]
    response = client.post("/api/meetings", json=invalid_data)
    assert response.status_code == 422
    assert "3時間以内" in response.json()["detail"]