---
marp: true
theme: default
size: 16:9
paginate: true
style: |
  section {
    justify-content: flex-start;
    padding: 130px 70px 70px;
    font-size: 26px;
  }
  section h1,
  section h2 {
    position: absolute;
    top: 48px;
    left: 70px;
    right: 70px;
    margin: 0;
    padding: 0 0 10px 18px;
    font-size: 34px;
    text-align: left;
    color: #1a4d8f;
    border-left: 8px solid #1a4d8f;
    border-bottom: 2px solid #d5dde8;
  }
  section.title {
    justify-content: center;
    text-align: center;
    padding: 70px;
  }
  section.title h1 {
    position: static;
    border: none;
    padding: 0;
    font-size: 52px;
    text-align: center;
    color: #1a4d8f;
  }
  section.toc ol {
    font-size: 30px;
    line-height: 1.8;
  }
  section.toc a {
    color: #1a4d8f;
    text-decoration: none;
    border-bottom: 1px dotted #1a4d8f;
  }
---

<!-- _class: title -->

# ヘッドレスCMS 入門

はじめて学ぶ人のための基礎知識

---

<!-- _class: toc -->

## 目次

1. [CMS とヘッドレスCMS](#3)
2. [従来型CMS との比較](#8)
3. [メリット](#11)
4. [デメリット・注意点](#15)
5. [主なサービスと構成](#18)
6. [導入判断と学習ステップ](#21)
7. [まとめ](#25)

---

## CMS とは

Web サイトの文章・画像を、専門知識がなくても
**管理・更新できる**システム

---

## 従来型CMS の構造

編集画面（Body）と表示部分（Head）が
**1つの製品にまとまっている**

> 例: WordPress、Drupal、Movable Type

| 部分 | 役割 |
| --- | --- |
| バックエンド（Body） | コンテンツの保存・管理・編集画面 |
| フロントエンド（Head） | コンテンツを HTML ページとして表示する部分 |

---

## ヘッドレスCMS とは

従来型CMS から **Head（表示部分）を切り離し**、
コンテンツ管理と API 配信に特化したCMS

- コンテンツは API（REST / GraphQL）経由で JSON として配信される
- 表示側（Web、アプリ、デジタルサイネージなど）は自由に実装できる
- 「Headless（頭がない）」＝ 表示部分を持たない、という意味

---

## 「Headless」の意味

Head（＝表示部分）を持たない
コンテンツは **API 経由で JSON として配信**される

---

## 構造の違い


```
[従来型]  編集画面 → DB → テンプレート → HTMLページ

[ヘッドレス]  編集画面 → DB → API(JSON)
                              ↓
              Web / アプリ / サイネージ / ...
```

---


## 比較①：配信先

従来型は基本的に **Webサイト1つ**
ヘッドレスは **複数チャネルへ同時配信**できる

---

## 比較②：技術の自由度

従来型はテンプレート言語に依存
ヘッドレスは **フロントエンド技術を自由に選べる**

---

## 比較③：手軽さ

従来型はすぐ公開できる
ヘッドレスは **フロント開発が前提**になる

---

## メリット① マルチデバイス配信

1つのコンテンツを
Web・アプリ・サイネージへ**同時に届けられる**

---

## メリット② フロントエンドの自由

React / Next.js / Vue / Nuxt など
**好きな技術**で実装できる

---

## メリット③ 表示が速い

静的サイト生成（SSG）と CDN 配信により
**高速なページ表示**を実現しやすい

---

## メリット④ セキュリティ

管理画面が公開サーバ上にないため
**攻撃対象が小さい**

---

## デメリット① 開発が必要

表示部分は自作するため
**開発者のリソースが必須**

---

## デメリット② プレビュー

「編集内容がどう見えるか」を
**別途仕組みとして用意**する必要がある

---

## デメリット③ 初期コスト

小規模サイトでは
従来型CMS の方が**早く安く済む**こともある

---

## 主なサービス

- 国産SaaS: microCMS、Newt
- 海外SaaS: Contentful、Sanity、Storyblok
- OSS: Strapi、Directus、Payload CMS
- Git ベース: Decap CMS、Tina CMS

---


## 一般的な構成例（Jamstack）

ヘッドレスCMS は「Jamstack」と呼ばれる構成でよく使われます。

```
編集者

  ↓ 入力

ヘッドレスCMS（microCMS など）

  ↓ Webhook（更新通知）

ホスティング（Vercel / Netlify）

  ↓ ビルド（Next.js などが API からコンテンツ取得）

CDN 配信 → 閲覧者
```

ポイント:

- コンテンツ更新をトリガーにサイトを自動ビルド・再配信する
- 閲覧者には CDN 上の静的ファイルが返るため高速

---

## 向いているケース

- 複数チャネルへ同じコンテンツを配信したい
- 表示速度・SEO を重視したい
- モダンなフロント技術で作りたい

---

## 向かないケース

- 小規模なコーポレートサイト・ブログ
- 開発リソースが限られている
- プラグインで手早く機能を揃えたい

---

## 学習ステップ

1. microCMS などに無料登録して API を触る
2. 返ってくる JSON の構造を確認する
3. Next.js で一覧・詳細ページを作る
4. デプロイし Webhook で自動ビルド設定

---

## 覚えておきたい用語

| 用語 | 意味 |
| --- | --- |
| Head | コンテンツを表示するフロントエンド部分 |
| API | システム間でデータをやり取りする窓口。REST / GraphQL が主流 |
| JSON | API のやり取りで使われるデータ形式 |
| SSG | 静的サイト生成。あらかじめ HTML を作っておく方式 |
| CDN | 世界各地のサーバから配信し高速化する仕組み |
| Webhook | イベント発生時に外部へ通知する仕組み |
| Jamstack | JavaScript・API・Markup を組み合わせたモダンな構成 |

---

## まとめ

ヘッドレスCMS は「**表示部分を持たない API 配信特化のCMS**」
規模と体制に応じて従来型CMS と使い分ける
