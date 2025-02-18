# ベースイメージ指定
FROM python:3.9-slim

# 作業ディレクトリ設定
WORKDIR /app

# 必要なファイルのコピー
COPY requirements.txt .
COPY pyproject.toml .

# システムの依存関係とPythonパッケージのインストール
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# アプリケーションコードのコピー
COPY . .

# Pythonパスの設定
ENV PYTHONPATH=/app

# ポートの公開
EXPOSE 8000

# アプリケーションの起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]