import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.utils import JST, to_utc
from .test_data import (
    get_valid_meeting_data,
    get_valid_task_data,
    get_invalid_meeting_data,
    VALID_STATUSES
)

class TestMeetings:
    def test_create_meeting(self, client):
        meeting_data = get_valid_meeting_data()
        response = client.post("/api/meetings", json=meeting_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == meeting_data["title"]
        assert data["participants"] == meeting_data["participants"]
        assert data["start_time"] == meeting_data["start_time"]
        assert data["end_time"] == meeting_data["end_time"]

    def test_create_meeting_invalid_time(self, client):
        invalid_data = get_invalid_meeting_data()["invalid_time_format"]
        response = client.post("/api/meetings", json=invalid_data)
        
        assert response.status_code == 422
        assert "時刻は HH:MM 形式で入力してください" in response.json()["detail"]

    def test_create_meeting_non_10min_interval(self, client):
        invalid_data = get_invalid_meeting_data()["non_10min_interval"]
        response = client.post("/api/meetings", json=invalid_data)
        
        assert response.status_code == 422
        assert "時刻は10分単位で指定してください" in response.json()["detail"]

    def test_create_meeting_end_before_start(self, client):
        invalid_data = get_invalid_meeting_data()["end_before_start"]
        response = client.post("/api/meetings", json=invalid_data)
        
        assert response.status_code == 422
        assert "終了時刻は開始時刻より後にしてください" in response.json()["detail"]

    def test_create_meeting_too_long(self, client):
        invalid_data = get_invalid_meeting_data()["too_long_duration"]
        response = client.post("/api/meetings", json=invalid_data)
        
        assert response.status_code == 422
        assert "会議時間は3時間以内にしてください" in response.json()["detail"]

    def test_get_meetings(self, client):
        # 会議を作成
        meeting_data = get_valid_meeting_data()
        client.post("/api/meetings", json=meeting_data)
        
        # 会議一覧を取得
        response = client.get("/api/meetings/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["title"] == meeting_data["title"]

    def test_get_meeting_by_id(self, client):
        # 会議を作成
        meeting_data = get_valid_meeting_data()
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["id"]
        
        # 作成した会議を取得
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == meeting_id
        assert data["title"] == meeting_data["title"]

    def test_update_meeting(self, client):
        # 会議を作成
        meeting_data = get_valid_meeting_data()
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["id"]
        
        # 会議を更新
        update_data = get_valid_meeting_data()
        update_data["title"] = "更新された会議"
        print(f"update_data: {update_data}")
        response = client.put(f"/api/meetings/{meeting_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新された会議"

    def test_delete_meeting(self, client):
        # 会議を作成
        meeting_data = get_valid_meeting_data()
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["id"]
        
        # 会議を削除
        response = client.delete(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        # 削除された会議を取得しようとする
        get_response = client.get(f"/api/meetings/{meeting_id}")
        assert get_response.status_code == 404

class TestTasks:
    def test_create_task(self, client):
        # 会議を作成
        meeting_data = get_valid_meeting_data()
        create_meeting_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_meeting_response.json()["id"]
        
        task_data = get_valid_task_data()
        response = client.post(f"/api/meetings/{meeting_id}/tasks/", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == task_data["content"]
        assert data["assignee"] == task_data["assignee"]
        assert data["status"] == task_data["status"]

    def test_get_meeting_tasks(self, client):
        # 会議とタスクを作成
        meeting_data = get_valid_meeting_data()
        create_meeting_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_meeting_response.json()["id"]
        
        task_data = get_valid_task_data()
        client.post(f"/api/meetings/{meeting_id}/tasks/", json=task_data)
        
        # タスク一覧を取得
        response = client.get(f"/api/meetings/{meeting_id}/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["content"] == task_data["content"]