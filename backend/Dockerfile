# ベースイメージ（お弁当箱）を選ぶ
FROM python:3.9-slim

# 作業ディレクトリ（お弁当を詰める場所）を作る
WORKDIR /app

# 必要なファイル（おかずの材料）をコピーする
COPY requirements.txt .
COPY pyproject.toml .

# Pythonパッケージ（おかず）をインストールします
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコード（できあがったおかず）をコピーします
COPY . .

# アプリケーションを起動（お弁当を開ける）する準備をします
EXPOSE 8000

# アプリケーションを起動（いただきます！）します
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]