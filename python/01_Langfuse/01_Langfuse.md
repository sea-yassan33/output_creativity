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

## 4-1.Docker_composeを実行 
```sh
# Docker_composeを実行
docker compose up -d

```

## 4-2.Dockerコマンド

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

## 4-3.トラブルシューティング

- 起動[compose up]の際にポート番号の競合が生じた際は下記で調べる
```sh
#Windows（cmd）
## 特定のポートで使用しているPIDを確認
netstat -ano | findstr :<port>

## 表示された PID を使って確認
tasklist | findstr <PID>

## 確認したPIDを終了
taskkill //PID <PID> //F

#Linux
## 特定のポートで使用しているPIDを確認
lsof -i :<port>

# プロセス名で検索
ps aux | grep python

## 確認したPIDを終了
kill -9 <PID>
```

- yamlで使用していないポート番号に変更する

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
CH_USER="yaml設定[CLICKHOUSE_USERの値]"
CH_PASSWORD="yaml設定[CLICKHOUSE_PASSWORDの値]"
CH_DB="yaml設定[CLICKHOUSE_DBの値]"
```

## 6-3．【例】コード

- [Python実装例](./01_Langfuse実装例.py)

# 7．databaseについて

- http://localhost:8123/play
  - yaml設定[CLICKHOUSE_USERの値]/yaml設定[CLICKHOUSE_PASSWORDの値]

- type(GENERATION)
```sql
SELECT *
FROM observations FINAL
where type = 'GENERATION';
```

- モデル別SQL
```sql
SELECT
  provided_model_name AS model,
  COUNT(*) AS call_count,
  SUM(usage_details['input']) AS total_input_tokens,
  SUM(usage_details['output']) AS total_output_tokens,
  SUM(usage_details['total']) AS total_tokens,
  SUM(total_cost) AS total_cost_usd
FROM observations FINAL
WHERE
  type = 'GENERATION'
  AND start_time >= '2025-01-01'
GROUP BY provided_model_name
ORDER BY total_cost_usd DESC;
```

- 日別、モデル別SQL
```sql
SELECT
  toDate(start_time) AS date,
  provided_model_name AS model,
  SUM(usage_details['input']) AS input_tokens,
  SUM(usage_details['output']) AS output_tokens,
  SUM(total_cost) AS cost_usd
FROM observations FINAL
WHERE
  type = 'GENERATION'
  AND start_time >= '2025-01-01'
GROUP BY date, model
ORDER BY date DESC, cost_usd DESC;
```

- タグ毎の抽出
```sql
SELECT observations.*, traces.tags
FROM observations FINAL
INNER JOIN traces FINAL ON observations.trace_id = traces.id
WHERE observations.type = 'GENERATION'
    AND hasAll(traces.tags, ['test260405']);
```

- タグ、日別、モデル別SQL①
```sql
SELECT
  toDate(observations.start_time) AS date,
  observations.provided_model_name AS model,
  traces.tags,
  SUM(observations.usage_details['input']) AS input_tokens,
  SUM(observations.usage_details['output']) AS output_tokens,
  SUM(observations.total_cost) AS cost_usd
FROM observations FINAL
INNER JOIN traces FINAL ON observations.trace_id = traces.id
WHERE
  observations.type = 'GENERATION'
  AND observations.start_time >= '2025-01-01'
GROUP BY date, model, traces.tags
ORDER BY date DESC, cost_usd DESC;
```

- タグ、日別、モデル別SQL②
```sql
SELECT
  toDate(observations.start_time) AS date,
  observations.provided_model_name AS model,
  groupArray(traces.tags) AS tags_list,
  SUM(observations.usage_details['input']) AS input_tokens,
  SUM(observations.usage_details['output']) AS output_tokens,
  SUM(observations.total_cost) AS cost_usd
FROM observations FINAL
INNER JOIN traces FINAL ON observations.trace_id = traces.id
WHERE
  observations.type = 'GENERATION'
  AND observations.start_time >= '2025-01-01'
GROUP BY date, model
ORDER BY date DESC, cost_usd DESC;
```

## pythonでDataBaseのデータを取得

- モジュールインストール
```
pip install clickhouse-connect
```

- [実装例:データを取得](./01_Langfuse_dataGet.py)

