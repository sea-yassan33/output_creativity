# 1．DB作成

## 前提条件

- Mysqltまたはmariadbが導入済みであること

## DB作成

```sh
## ログイン
mysql -u root -p
## データベース作成
CREATE DATABASE strapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
## 新しいユーザーの作成
CREATE USER 'strapi_user'@'localhost' IDENTIFIED BY 'strapi_user';
## 権限の付与
GRANT ALL PRIVILEGES ON strapi_db.* TO 'strapi_user'@'localhost';
## 設定の反映
FLUSH PRIVILEGES;

```

### 上記のコマンドについて

| コマンド | 意味 |
| --- | --- |
| `mysql -u root -p` | **MySQLにログイン。** 管理者（root）として入ります。`-p`を付けているので、実行後にパスワードを求められます。 |
| `CREATE DATABASE strapi_db ...` | **データベース作成。** 名前は `strapi_db` です。文字コードを `utf8mb4` にすることで、絵文字なども保存可能になります。 |
| `CREATE USER 'strapi_user'@'localhost' ...` | **新しいユーザーの作成。** `strapi_user` という名前のユーザーを作り、パスワードを設定します。 |
| `GRANT ALL PRIVILEGES ON ...` | **権限の付与。** 作成したユーザーに対して、`strapi_db` 内のすべての操作を許可します。 |
| `FLUSH PRIVILEGES;` | **設定の反映。** 変更した権限設定を即座に有効化します。 |

