class BaseAppException(Exception):
    """アプリケーションの基本例外クラス"""
    def __init__(self, message: str, status_code: int = 422):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# バリデーション関連の例外
class ValidationError(BaseAppException):
    """入力値の検証に失敗した場合の例外"""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)

class DateValidationError(ValidationError):
    """日付の検証に失敗した場合の例外"""
    def __init__(self):
        super().__init__(message="過去の日付は指定できません。未来の日付を入力してください。")

class ContentLengthError(ValidationError):
    """内容の長さが制限を超えた場合の例外"""
    def __init__(self, max_length: int):
        super().__init__(message=f"内容は{max_length}文字以内で入力してください。")

# リソース関連の例外
class ResourceNotFound(BaseAppException):
    """要求されたリソースが見つからない場合の例外"""
    def __init__(self, resource_name: str):
        super().__init__(
            message=f"{resource_name}が見つかりませんでした。",
            status_code=404
        )

class ResourceConflict(BaseAppException):
    """リソースの重複や競合が発生した場合の例外"""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)

# 認証・認可関連の例外
class AuthenticationError(BaseAppException):
    """認証に失敗した場合の例外"""
    def __init__(self):
        super().__init__(
            message="認証に失敗しました。",
            status_code=401
        )

class AuthorizationError(BaseAppException):
    """権限がない操作を試みた場合の例外"""
    def __init__(self):
        super().__init__(
            message="この操作を行う権限がありません。",
            status_code=403
        )