# 会議議事録自動生成アプリ

## 概要
会議の議事録を効率的に作成・管理できるWebアプリケーションです。音声認識とAIを活用した自動文字起こし・要約機能により、会議のドキュメント化を効率的にします。

## 主な機能
### 実装済み
- 会議管理基本機能
  - 会議の作成・編集・削除
  - 参加者管理
  - 日時管理（バリデーション付き）
- タスク管理機能
  - 会議からのタスク作成
  - 担当者アサイン
  - ステータス管理
- Docker/Docker Compose による環境構築
  - 開発/本番環境の分離
  - PostgreSQLコンテナ化
- CI/CD基盤
  - GitHub Actionsによる自動テスト
  - Docker Hubへの自動デプロイ

### 実装予定
- ユーザー認証（JWT）
  - セキュアなログイン機能
  - ロールベースのアクセス制御
- 音声認識による文字起こし機能
- AWS環境でのデプロイ
  - Elastic Beanstalkを使用
  - Blue-Greenデプロイメント
  - CloudWatchによる監視

## 技術スタック
### バックエンド
- Python 3.9
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic（マイグレーション）

### フロントエンド
- Vue 3
- Tailwind CSS

### インフラ/開発環境
- Docker / Docker Compose
- GitHub Actions
- AWS（予定）
  - Elastic Beanstalk
  - RDS
  - CloudWatch

## アーキテクチャの特徴
- マイクロサービスを意識した設計
- 環境変数による構成管理
- エラーハンドリングの一元化
- バリデーションの厳格な実装
- OpenAPIによるAPI仕様の自動生成

## テスト
- unittest/pytestによる自動テスト
- テストカバレッジ目標：80%以上
- GitHub Actionsでの自動テスト実行

## 開発背景
会議の議事録作成には多くの時間と労力が必要とされ、その後のタスク管理も含めると業務効率に大きな影響を与えます。このアプリケーションは、そうした課題を解決し、チームの生産性向上を支援することを目的としています。

## 今後の展望
- リアルタイムコラボレーション機能
- AIを活用した会議要約の最適化
- チーム別のカスタマイズ機能
- モバイルアプリの開発

## ローカル環境での実行方法
```bash
# リポジトリのクローン
git clone https://github.com/luckylundy/meeting_minutes.git
cd meeting_minutes

# 開発環境の起動
docker-compose up -d

# マイグレーションの実行
docker-compose exec backend alembic upgrade head

## コントリビューション
Issue、Pull Requestは大歓迎です。改善のご提案やバグ報告など、お気軽にご連絡ください。
