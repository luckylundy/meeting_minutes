from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # フロントエンドのURL
    allow_credentials=True,  # クッキー等の認証情報を許可
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Meeting Minutes API"}