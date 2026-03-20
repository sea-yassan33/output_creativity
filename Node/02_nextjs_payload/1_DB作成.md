# PostgreSQLでDB作成

## DB作成
```sh
## ログイン
psql -U postgres

## データベース作成
CREATE DATABASE nextpay_db ENCODING 'UTF8';

## 新しいユーザー（ロール）の作成
CREATE USER sample_user WITH PASSWORD 'sample_pw';

## 権限の付与
GRANT ALL PRIVILEGES ON DATABASE nextpay_db TO sample_user;

## 【PostgreSQL15以降】スキーマへの権限付与も必要
ALTER DATABASE nextpay_db OWNER TO sample_user;

## ログアウト
\q

## 再度ログインできるか確認
psql -U sample_user -d nextpay_db
```

|コマンド|何ができるか|
|:----|:----|
|\l|データベースの一覧を表示する|
|\c DB名|指定したデータベースに**接続（切り替え）する|
|\dt|現在のDBにあるテーブル一覧**を表示する|
|\d テーブル名|テーブルの**列構成（型や制約）**を確認する|
|\du|ユーザー（ロール）一覧を表示する|
|\q|psqlを**終了（ログアウト）**する|