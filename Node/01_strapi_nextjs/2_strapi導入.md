# 2.Strapiの導入

## Strapiを導入
```sh
npx create-strapi-app@latest project-cms

? Please log in or sign up. Skip
? Do you want to use the default database (sqlite) ? No
? Choose your default database client mysql
? Database name: strapi_db
? Host: {IPアドレス}
? Port: ｛ポート番号｝
? Username: {ユーザー名}
? Password: ***********
? Enable SSL connection: No
? Start with an example structure & data? No
? Start with Typescript? Yes
? Install dependencies with npm? Yes
? Initialize a git repository? No
? Participate in anonymous A/B testing (to improve Strapi)? No
```

## 必要なモジュールインストール
```sh
cd project-cms
npm install mysql2
```

## 初期設定
- my-project\src\admin\app.tsx

```tsx
import type { StrapiApp } from '@strapi/strapi/admin';

export default {
  config: {
    locales: [
      'ja',
    ],
  },
  bootstrap(app: StrapiApp) {
    console.log(app);
  },
};

```

```sh
## 構築
npm run build
## 起動
npm run develop
```

## ログイン画面

http://localhost:1337

![ログイン画面](https://i.gyazo.com/2c907e825193cd2b05e09ef9bbb10ff9.png)

- 下記必須項目
  - First name
  - Email(ダミーでもOK)
  - Password(大文字、数字、英字を含めた8文字以上)
  - チェックボックスはなしでOK

- 日本語化
  - 左下をクリック
  - Profile settingsをクリック
  - ExperienceのInterface languageを「日本語」に選択
  - Save

## Collection Typesを作成

- 「Content-Type Builder」をクリック
- 「＋（新しいContent-Typeを作成）」をクリック
![CollectionTypesを作成](https://i.gyazo.com/fda96cd02c86289e62fc54a2a6f4522a.png)

- 「フィールドを追加」をクリック

![フィールドの種類](https://i.gyazo.com/2a414ad8ef0f684cee7589f9a1a4c262.png)

- Enumeration（カテゴリー）
![カテゴリー](https://i.gyazo.com/c4bcc79fe40f578863d87585252e44d3.png)

## 権限の変更

- 権限の変更
  - setting
  - Users & Permissions plugin
  - Roles
  - Public
  - 「作成したContent-Type」の▼をクリック
  - 「find」・「findOne」

![権限変更](https://i.gyazo.com/70e73f0f966e9f540c8b3156c1c24d92.png)


## 記事を作成

- 「Content Manager」
- 「作成したContent-Type」
- 「Create new entry」
- 「Save」は上書き
- 「Publish」は公開

![記事を作成](https://i.gyazo.com/92601203146faa4db4afcf38e0902bc9.png)]

## API呼び出し

- 呼び出し例（作成したContent-Type{notices}の全コンテンツ）
http://localhost:1337/api/notices?sort=publishedDate:desc


### filterの方法

https://docs.strapi.io/cms/api/rest/filters


- エンドポイントでフィルター機能（filters）を使用する際の基本的な書き方をまとめます。

1. 基本的な構文
```sh
GET /api/notices?filters[フィールド名][$演算子]=値
```

2. よく使われるフィルター例

```sh
## 完全一致 ($eq): タイトルが「重要」なものを取得
GET /api/{Content-Type}?filters[title][$eq]=重要

## 部分一致 ($contains): タイトルに「アップデート」を含むものを取得
GET /api/{Content-Type}?filters[title][$contains]=アップデート

## より大きい/小さい ($gt, $lt): IDが10より大きいものを取得
GET /api/{Content-Type}?filters[id][$gt]=10

## 複数条件 (AND): カテゴリが news かつ IDが5より大きい
GET /api/{Content-Type}?filters[type][$eq]=news&filters[id][$gt]=5
```

3. 主な演算子一覧

| 演算子 | 内容 |
|---|---|
| $eq | 等しい |
| $ne | 等しくない |
| $lt, $lte | 未満、以下 |
| $gt, $gte | 超過、以上 |
| $contains | 含む（大文字小文字を区別する） |
| $notContains | 含まない |
| $in, $notIn | 配列内の値に含まれる / 含まれない |
| $null, $notNull | Nullである / Nullでない |


## リッチエディタ

https://www.npmjs.com/package/@ckeditor/strapi-plugin-ckeditor