# Payload導入

## 1.プロジェクト生成

```sh
npm create payload-app@latest

> npx
> create-payload-app
┌   create-payload-app
◇  Project name?
│  nextjs-payload
◇  Choose project template
│  blank
◇  Select a database
│  PostgreSQL
◆  Enter PostgreSQL connection string
│  postgres://sample_user:sample_pw@127.0.0.1:5432/nextpay_db

```
## 2.TailsindCSSの導入

### TailsindCSS関連のモジュールをインストール

- 下記のコマンドで関連のモジュールをインストール
```sh
npm install tailwindcss @tailwindcss/postcss postcss
```

- 【新規作成】postcss.config.mjs
```js
// postcss.config.mjs
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
```

### globals.cssなどにTailwindを読み込ませる

- src\app\(frontend)\globals.css
  - [サンプル](./globals.css)

### shadcn/ui の導入

- 下記のコマンドで関連のモジュールをインストール
```sh
## ui.shadcn
## https://ui.shadcn.com/
npx shadcn@latest init -d
npx shadcn@latest add  button card badge separator

```

## 3.Payload Collections の作成

### Users コレクション（認証用）の作成

- src\collections\Users.ts

```ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  admin: {
    useAsTitle: 'email',
  },
  fields: [
    {
      name: 'name',
      type: 'text',
      required: true,
      label: '名前',
    },
  ],
}
```

### Posts コレクション（ブログ記事）の作成

- src\collections\Posts.ts

```ts
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'status', 'publishedAt', 'author'],
  },
  access: {
    read: () => true,
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
      label: 'タイトル',
    },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
      label: 'スラッグ（URL用）',
      admin: {
        description: '半角英数字とハイフンのみ使用可能（例: my-first-post）',
      },
    },
    {
      name: 'excerpt',
      type: 'textarea',
      label: '概要（一覧に表示）',
    },
    {
      name: 'content',
      type: 'richText',
      required: true,
      label: '本文',
    },
    {
      name: 'thumbnail',
      type: 'upload',
      relationTo: 'media',
      label: 'サムネイル画像',
    },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
      label: '著者',
    },
    {
      name: 'categories',
      type: 'relationship',
      relationTo: 'categories',
      hasMany: true,
      label: 'カテゴリ',
    },
    {
      name: 'status',
      type: 'select',
      options: [
        { label: '下書き', value: 'draft' },
        { label: '公開', value: 'published' },
      ],
      defaultValue: 'draft',
      required: true,
      label: '公開ステータス',
    },
    {
      name: 'publishedAt',
      type: 'date',
      label: '公開日時',
      admin: {
        date: {
          pickerAppearance: 'dayAndTime',
        },
      },
    },
  ],
}
```

### Categories コレクションの作成

- src\collections\Categories.ts

```ts
import type { CollectionConfig } from 'payload'

export const Categories: CollectionConfig = {
  slug: 'categories',
  admin: {
    useAsTitle: 'name',
  },
  access: {
    read: () => true,
  },
  fields: [
    {
      name: 'name',
      type: 'text',
      required: true,
      label: 'カテゴリ名',
    },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
      label: 'スラッグ',
    },
  ],
}
```

### Media コレクション（画像アップロード）の作成

- src\collections\Media.ts

```ts
import type { CollectionConfig } from 'payload'
import path from 'path'
import { fileURLToPath } from 'url'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true,
  },
  upload: {
    staticDir: path.resolve(dirname, '../../public/media'),
    imageSizes: [
      {
        name: 'thumbnail',
        width: 400,
        height: 300,
        position: 'centre',
      },
      {
        name: 'card',
        width: 768,
        height: 512,
        position: 'centre',
      },
    ],
    adminThumbnail: 'thumbnail',
    mimeTypes: ['image/*'],
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      label: 'Alt テキスト',
    },
  ],
}
```

## 4.Payload 設定ファイルの更新

### 設定概要

- 日本語設定を有効化
- メール機能を無効化
- Collectionsのマイグレーション設定

### 必要なモジュールをインストール

```sh
npm install @payloadcms/translations
npm add @payloadcms/email-nodemailer nodemailer
npm i --save-dev @types/nodemailer
```

### 設定ファイルの修正

- src\payload.config.ts

```ts
import { buildConfig } from 'payload'
import { postgresAdapter } from '@payloadcms/db-postgres'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import { nodemailerAdapter } from '@payloadcms/email-nodemailer'
import nodemailer from 'nodemailer'
import path from 'path'
import { fileURLToPath } from 'url'
import sharp from 'sharp'
// 以下：作成したColectionsを読み込ませる
import { Users } from './collections/Users'
import { Posts } from './collections/Posts'
import { Categories } from './collections/Categories'
import { Media } from './collections/Media'
// 以下：英語と日本語を使える様にモジュール読み込ませる
import { en } from '@payloadcms/translations/languages/en'
import { ja } from '@payloadcms/translations/languages/ja'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    user: Users.slug,
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  collections: [Users, Posts, Categories, Media],
  editor: lexicalEditor(),
  secret: process.env.PAYLOAD_SECRET || '',
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  db: postgresAdapter({
    pool: {
      connectionString: process.env.DATABASE_URL || '',
    },
  }),
  sharp,
  plugins: [],
  serverURL: process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:3000',
  i18n: {
    supportedLanguages: { en,ja },
  },
  email: nodemailerAdapter({
    defaultFromAddress: 'noreply@example.com',
    defaultFromName: 'No Reply',
    transport: nodemailer.createTransport({ jsonTransport: true }),
  }),
})
```

### 型の自動生成

- Payload CMSのコレクションやグローバル設定（payload.config.ts）を基に、対応するTypeScriptのインターフェース（.ts型定義ファイル）を自動生成するコマンドです。

```sh
npx payload generate:types
```

## 5．フロント画面の実装

### Payloadクライアントユーティリティ作成

- src\lib\payload.ts

```ts
import configPromise from '@payload-config'
import { getPayload } from 'payload'

export async function getPayloadClient() {
  const payload = await getPayload({ config: configPromise })
  return payload
}
```

###  RichTextレンダリング用コンポーネントを作成

- src\components\parts\richText.tsx

```tsx
import type { DefaultNodeTypes } from '@payloadcms/richtext-lexical'
import type { SerializedEditorState } from '@payloadcms/richtext-lexical/lexical'
import {type JSXConvertersFunction,RichText as RichTextConverter,} from '@payloadcms/richtext-lexical/react'
import { JSX } from 'react'

const jsxConverters: JSXConvertersFunction<DefaultNodeTypes> = ({ defaultConverters }) => ({
  ...defaultConverters,

  // 見出し
  heading: ({ node, nodesToJSX }) => {
    const children = nodesToJSX({ nodes: node.children })

    const styles: Record<string, string> = {
      h1: 'text-4xl font-extrabold text-gray-900 mt-10 mb-4',
      h2: 'text-4xl font-bold text-gray-800 mt-8 mb-3 border-b-2 border-gray-200 pb-2',
      h3: 'text-2xl font-semibold text-gray-700 mt-6 mb-2',
      h4: 'text-xl font-semibold text-gray-600 mt-4 mb-2',
    }

    const Tag = node.tag as keyof JSX.IntrinsicElements
    return <Tag className={styles[node.tag] ?? ''}>{children}</Tag>
  },

  // 段落
  paragraph: ({ node, nodesToJSX }) => (
    <p className="text-base leading-8 text-gray-700 mb-4">
      {nodesToJSX({ nodes: node.children })}
    </p>
  ),

  // 引用
  quote: ({ node, nodesToJSX }) => (
    <blockquote className="border-l-4 border-blue-400 pl-4 italic text-gray-500 my-4">
      {nodesToJSX({ nodes: node.children })}
    </blockquote>
  ),
})

type Props = {
  data: SerializedEditorState
  className?: string
}

export function RichText({ data, className }: Props) {
  return (
    <RichTextConverter
      converters={jsxConverters}
      data={data}
      className={className}
    />
  )
}
```

### ブログ一覧ページ

- [【サンプル】ブログ一覧ページ](./sample/blog/page.tsx)

### ブログ詳細ページ

- [【サンプル】ブログ詳細ページ](./sample/blog/[slug]/page.tsx)

### フロントエンド用レイアウト

- src\app\(frontend)\layout.tsx

```tsx
import React from 'react'
import Link from 'next/link'
import type { Metadata } from 'next'
import "./globals.css";

export const metadata: Metadata = {
  title: 'My Blog',
  description: 'Payload CMS で作るブログ',
}

export default async function RootLayout(props: { children: React.ReactNode }) {
  const { children } = props

  return (
    <html lang="ja">
      <body>
      <header className="border-b">
          <div className="container mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
            <Link href="/" className="text-xl font-bold">
              My Blog
            </Link>
            <nav>
              <Link href="/blog" className="text-sm hover:underline mx-2">
                記事一覧
              </Link>
              <Link href="/admin" className="text-sm hover:underline">
                管理画面
              </Link>
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="border-t mt-16">
          <div className="container mx-auto max-w-5xl px-4 py-6 text-center text-sm text-muted-foreground">
            © 2025 My Blog. Powered by Payload CMS + Next.js
          </div>
        </footer>
      </body>
    </html>
  )
}
```

## 6.DBマイグレーション

```sh
## 依存パッケージのインストール
npm install

## 新規マイグレーション作成
npm run payload migrate:create

## DB マイグレーションの実行
###まだ実行されていないすべてのマイグレーションを実行
npm run payload migrate

# ======= 以下：マイグレーションのコマンド

## マイグレーション状態
npm run payload migrate:status

## 前回の移行処理をロールバック
npm run payload migrate:down

## 既に実行済みの移行をすべてロールバックし、再度実行
npm run payload migrate:refresh

## データベースからすべてのエンティティを削除し、すべてのマイグレーションを最初から再実行
npm run payload migrate:fresh

```

## 7.動作確認

### 開発サーバーの起動

```sh
## 開発サーバーの起動
npm run dev

```

### 管理画面アクセス＞初期ユーザー登録＞日本語設定＞記事登録

1. ブラウザで `http://localhost:3000/admin` を開く
2. 「Create your first user」画面で管理者ユーザーを登録
3. ブラウザで`http://localhost:3000/admin/account`を開く
4. language > 日本語
5. ログインおよび設定後、管理画面から記事・カテゴリを作成

### 記事登録確認

1. ブラウザで `http://localhost:3000/blog` を開く
2. 以下サンプル動画

![サンプル動画](https://i.gyazo.com/f783a6e71c1205b61929fd45c0b53560.gif)

