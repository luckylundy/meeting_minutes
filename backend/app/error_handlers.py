from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError
from .exceptions import BaseAppException  # 基底クラスのみをインポート
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

async def app_exception_handler(request: Request, exc: BaseAppException):
    """アプリケーション独自の例外をハンドリング"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "status_code": exc.status_code,
            "path": request.url.path,
            "type": exc.__class__.__name__  # エラーの種類も含める
        }
    )

async def validation_exception_handler(request: Request, exc: PydanticValidationError):
    """Pydanticのバリデーションエラーをハンドリング"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "入力データが不正です",
            "details": exc.errors(),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "path": request.url.path,
            "type": "ValidationError"
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """データベースエラーをハンドリング"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "データベース処理中にエラーが発生しました",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "path": request.url.path,
            "type": "DatabaseError"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """予期せぬエラーをハンドリング"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "予期せぬエラーが発生しました",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "path": request.url.path,
            "type": "UnexpectedError"
        }
    )