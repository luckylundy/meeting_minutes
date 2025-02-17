from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError
from .exceptions import BaseAppException
import logging

logger = logging.getLogger(__name__)

async def app_exception_handler(request: Request, exc: BaseAppException):
    """アプリケーション独自の例外をハンドリング"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message
        }
    )

async def validation_exception_handler(request: Request, exc: PydanticValidationError):
    """Pydanticのバリデーションエラーをハンドリング"""
    errors = exc.errors()
    logger.error(f"Validation Errors: {errors}")
    
    # エラーメッセージを取得
    if len(errors) > 0:
        error = errors[0]
        if isinstance(error.get("msg"), str):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": error.get("msg")}
            )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "入力データが不正です"}
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """データベースエラーをハンドリング"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "データベース処理中にエラーが発生しました"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """予期せぬエラーをハンドリング"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "予期せぬエラーが発生しました"
        }
    )