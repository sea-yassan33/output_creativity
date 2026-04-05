# 1.LangFuseについて

- https://langfuse.com/jp
- https://github.com/langfuse/langfuse

- Langfuse は、LLM（大規模言語モデル）を活用したソフトウェア開発のために設計された、オープンソースの観測・分析プラットフォームです。
- 開発者や企業が LLM アプリケーションを円滑に構築・改善できるよう、高度なトレーシング（追跡）機能や分析ツールを提供し、モデルのコスト、品質、レイテンシ（応答時間）に関する深い洞察をお届けします。

- [生成AIアプリの出力をRagasで評価して、LangfuseでGUI監視しよう！](https://qiita.com/minorun365/items/70ad2f5a0afaac6e5cb9)
- [LLMアプリの料金設計とLangfuseを活用した分析設計](https://www.youtube.com/watch?v=kTIFd6cby_I)

# 2.ローカル環境構築方法

```sh
# 1. リポジトリをクローン
git clone https://github.com/langfuse/langfuse.git

# 2.移動
cd langfuse

```

# 3.yaml設定

- 以下既にPostgreSQLある場合に設定を変更

```sh
postgres:
  image: docker.io/postgres:${POSTGRES_VERSION:-17}
  restart: always
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 3s
    timeout: 3s
    retries: 10
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-postgres}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
    POSTGRES_DB: ${POSTGRES_DB:-postgres}
    TZ: UTC
    PGTZ: UTC
  ports:
    - 127.0.0.1:｛ポート番号を変更｝:5432 # ポート番号を変更
  volumes:
    - langfuse_postgres_data:/var/lib/postgresql/data
```

# 4.Docker_composeを実行

```sh
# 起動
docker compose up

# バックグラウンド実行
docker compose up -d

# 停止
docker compose down

# コンテナの状態を表示
docker compose ps

# 初期化
docker compose down -v
```

# 5.Docker_composeを実行後

- 下記にアクセス
  - http://localhost:3000

## 5-1.アカウント作成
- サインアップ
  - ユーザ名
  - メールアドレス
  - パスワード(英数字・特殊文字・８文字以上)

## 5-2.組織の作成
- 「+ New Organization」をクリック

## 5-3.プロジェクトを作成
- 「+ New Project」をクリック

## 5-4.APIキーの作成
- 「Create new API keys」を選択

# 6.pythonで実装

## 6-1.モジュールインストール
下記をインストール
```sh
pip install langfuse
```

## 6-2.envファイルの設定
```sh
LANGFUSE_SECRET_KEY="secretキーを設定"
LANGFUSE_PUBLIC_KEY="publicキーを設定"
LANGFUSE_BASE_URL="http://localhost:3000"
```

## 6-3．【例】コード

- [Python実装例](./01_Langfuse実装例.py)

# 7．A5:SQL設定

| 項目 | 値 |
|---|---|
| ホスト | `localhost` |
| ポート | `5433` |
| データベース名 | `postgres` |
| ユーザー名 | `postgres` |
| パスワード | `postgres` |