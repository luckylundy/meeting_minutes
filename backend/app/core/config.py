# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pydantic import ConfigDict

class Settings(BaseSettings):
    # 基本設定
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # アプリケーション情報
    APP_TITLE: str = "会議議事録自動生成アプリ"
    APP_DESCRIPTION: str = "会議の記録と議事録を自動で生成するためのAPI"
    APP_VERSION: str = "1.0.0"
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./meeting_minutes.db"
    
    # class Config: の代わりに
    model_config = ConfigDict(
        env_file=".env"
    )

@lru_cache()
def get_settings():
    return Settings()