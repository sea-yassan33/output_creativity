# PostgreSQL導入方法

## インストーラをダウンロード

https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

![インストーラ](https://i.gyazo.com/690037439de8aae9eaa515cdad3f174b.png)

- [インストール方法](https://qiita.com/tom-sato/items/037b8f8cb4b326710f71)

## 基本的なコマンド

```sh
# ログイン
psql -U postgres

psql -U ユーザー名 -d データベース名

## db作成
CREATE DATABASE {db};

## db削除
drop database {db};

## テーブル削除
DROP TABLE IF EXISTS テーブル名;
```

|コマンド|何ができるか|
|:----|:----|
|\l|データベースの一覧を表示する|
|\c DB名|指定したデータベースに**接続（切り替え）する|
|\dt|現在のDBにあるテーブル一覧**を表示する|
|\d テーブル名|テーブルの**列構成（型や制約）**を確認する|
|\du|ユーザー（ロール）一覧を表示する|
|\q|psqlを**終了（ログアウト）**する|


## DB作成
```sh
## ログイン
psql -U postgres

## データベース作成
CREATE DATABASE strapi_db ENCODING 'UTF8';

## 新しいユーザー（ロール）の作成
CREATE USER strapi_user WITH PASSWORD 'strapi_user';

## 権限の付与
GRANT ALL PRIVILEGES ON DATABASE strapi_db TO strapi_user;

## PostgreSQL 15以降は、スキーマへの権限付与も必要になる場合があります
ALTER DATABASE strapi_db OWNER TO strapi_user;
```


## pgvectorのインストール＆ビルド
- x64 Native Tools Command Promptを**管理者権限**で開く(Winsows検索メニューから検索すると出てくる)

https://github.com/pgvector/pgvector

```sh
## PostgreSQLのインストール先を指定（ご自身の環境に合わせてください）
set "PGROOT=C:\Program Files\PostgreSQL\16"

## ソースを取得してビルド
cd %TEMP%
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install
```
## DB作成し拡張機能 pgvectorの拡張機能 を有効化

```
CREATE DATABASE langchain_db;

\c langchain_db;

CREATE EXTENSION IF NOT EXISTS vector;
```
