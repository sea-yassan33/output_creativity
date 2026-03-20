# Next.js + Payload CMS ブログ作成手順書

> **技術スタック**  
> Next.js（最新） / TypeScript / TailwindCSS / shadcn/ui / Payload CMS / PostgreSQL

---

## 目次

1. [前提条件・環境確認](#1-前提条件環境確認)
2. [Payload アプリの作成](#2-payload-アプリの作成)
3. [PostgreSQL の設定](#3-postgresql-の設定)
4. [TailwindCSS の導入](#4-tailwindcss-の導入)
5. [shadcn/ui の導入](#5-shadcnui-の導入)
6. [Payload Collections の作成](#6-payload-collections-の作成)
7. [ブログ一覧・詳細ページの実装](#7-ブログ一覧詳細ページの実装)
8. [動作確認](#8-動作確認)
9. [ディレクトリ構成（最終）](#9-ディレクトリ構成最終)

---

## 1. 前提条件・環境確認

以下がインストールされていることを確認してください。

| ツール | 推奨バージョン | 確認コマンド |
|--------|--------------|-------------|
| Node.js | 20.x 以上 | `node -v` |
| pnpm | 9.x 以上 | `pnpm -v` |
| PostgreSQL | 15.x 以上 | `psql --version` |

### pnpm がない場合のインストール

```bash
npm install -g pnpm
```

---

## 2. Payload アプリの作成

### 2-1. プロジェクト生成

```bash
pnpm create payload-app@latest
```

対話形式で以下を入力します。

| 質問 | 入力値 |
|------|--------|
| Project name | `my-blog`（任意） |
| Select a template | `blank` |
| Select a database | `PostgreSQL` |
| Would you like to use TypeScript? | `Yes` |

> 生成完了後、プロジェクトディレクトリに移動します。

```bash
cd my-blog
```

### 2-2. 生成直後のディレクトリ確認

```
my-blog/
├── src/
│   ├── app/
│   │   ├── (payload)/        # Payload 管理画面ルート
│   │   └── (frontend)/       # フロントエンドルート（後で作成）
│   ├── collections/          # Payload コレクション定義
│   └── payload.config.ts     # Payload 設定ファイル
├── .env
├── next.config.mjs
├── package.json
└── tsconfig.json
```

---

## 3. PostgreSQL の設定

### 3-1. データベース作成

```bash
psql -U postgres
```

```sql
CREATE DATABASE my_blog_db;
CREATE USER my_blog_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE my_blog_db TO my_blog_user;
\q
```

### 3-2. 環境変数の設定

プロジェクトルートの `.env` を編集します。

```env
# .env

DATABASE_URI=postgresql://my_blog_user:your_password@localhost:5432/my_blog_db
PAYLOAD_SECRET=your-super-secret-key-change-this-in-production

# Next.js
NEXT_PUBLIC_SERVER_URL=http://localhost:3000
```

> `PAYLOAD_SECRET` は本番環境では必ず強固なランダム文字列に変更してください。

---

## 4. TailwindCSS の導入

Payload のテンプレートによっては未導入の場合があるため、手動で設定します。

### 4-1. パッケージのインストール

```bash
pnpm add -D tailwindcss @tailwindcss/typography postcss autoprefixer
pnpm dlx tailwindcss init -p
```

### 4-2. `tailwind.config.ts` の設定

```ts
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

export default config
```

### 4-3. グローバル CSS の設定

```css
/* src/app/(frontend)/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 5. shadcn/ui の導入

### 5-1. 初期化

```bash
pnpm dlx shadcn@latest init
```

対話形式で以下を入力します。

| 質問 | 入力値 |
|------|--------|
| Which style would you like to use? | `Default` |
| Which color would you like to use as base color? | `Slate` |
| Would you like to use CSS variables for colors? | `Yes` |

### 5-2. よく使うコンポーネントの追加

```bash
pnpm dlx shadcn@latest add button card badge separator
```

---

## 6. Payload Collections の作成

### 6-1. Users コレクション（認証用）

```ts
// src/collections/Users.ts
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

### 6-2. Posts コレクション（ブログ記事）

```ts
// src/collections/Posts.ts
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

### 6-3. Categories コレクション

```ts
// src/collections/Categories.ts
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

### 6-4. Media コレクション（画像アップロード）

```ts
// src/collections/Media.ts
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

### 6-5. Payload 設定ファイルの更新

```ts
// src/payload.config.ts
import { buildConfig } from 'payload'
import { postgresAdapter } from '@payloadcms/db-postgres'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { fileURLToPath } from 'url'
import sharp from 'sharp'

import { Users } from './collections/Users'
import { Posts } from './collections/Posts'
import { Categories } from './collections/Categories'
import { Media } from './collections/Media'

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
      connectionString: process.env.DATABASE_URI || '',
    },
  }),
  sharp,
  serverURL: process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:3000',
})
```

---

## 7. ブログ一覧・詳細ページの実装

### 7-1. Payload クライアントユーティリティ

```ts
// src/lib/payload.ts
import configPromise from '@payload-config'
import { getPayload } from 'payload'

export async function getPayloadClient() {
  const payload = await getPayload({ config: configPromise })
  return payload
}
```

### 7-2. ブログ一覧ページ

```tsx
// src/app/(frontend)/blog/page.tsx
import Link from 'next/link'
import { getPayloadClient } from '@/lib/payload'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Post } from '@/payload-types'

export const dynamic = 'force-dynamic'

export default async function BlogPage() {
  const payload = await getPayloadClient()

  const { docs: posts } = await payload.find({
    collection: 'posts',
    where: {
      status: { equals: 'published' },
    },
    sort: '-publishedAt',
    depth: 2,
  })

  return (
    <main className="container mx-auto max-w-5xl px-4 py-12">
      <h1 className="mb-8 text-4xl font-bold tracking-tight">ブログ</h1>

      {posts.length === 0 ? (
        <p className="text-muted-foreground">記事がまだありません。</p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {posts.map((post) => (
            <PostCard key={post.id} post={post as Post} />
          ))}
        </div>
      )}
    </main>
  )
}

function PostCard({ post }: { post: Post }) {
  const author = typeof post.author === 'object' ? post.author : null
  const categories = post.categories?.filter((c) => typeof c === 'object') ?? []

  return (
    <Card className="flex flex-col hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="mb-2 flex flex-wrap gap-1">
          {categories.map((cat: any) => (
            <Badge key={cat.id} variant="secondary">
              {cat.name}
            </Badge>
          ))}
        </div>
        <CardTitle className="text-lg leading-snug">
          <Link href={`/blog/${post.slug}`} className="hover:underline">
            {post.title}
          </Link>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1">
        {post.excerpt && (
          <p className="text-sm text-muted-foreground line-clamp-3">{post.excerpt}</p>
        )}
      </CardContent>

      <CardFooter className="text-xs text-muted-foreground flex justify-between">
        <span>{author?.name ?? '不明'}</span>
        {post.publishedAt && (
          <span>
            {new Date(post.publishedAt).toLocaleDateString('ja-JP', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </span>
        )}
      </CardFooter>
    </Card>
  )
}
```

### 7-3. ブログ詳細ページ

```tsx
// src/app/(frontend)/blog/[slug]/page.tsx
import { notFound } from 'next/navigation'
import { getPayloadClient } from '@/lib/payload'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import Link from 'next/link'

interface Props {
  params: { slug: string }
}

export async function generateStaticParams() {
  const payload = await getPayloadClient()
  const { docs } = await payload.find({
    collection: 'posts',
    where: { status: { equals: 'published' } },
    limit: 100,
  })
  return docs.map((post) => ({ slug: post.slug }))
}

export default async function BlogDetailPage({ params }: Props) {
  const payload = await getPayloadClient()

  const { docs } = await payload.find({
    collection: 'posts',
    where: {
      slug: { equals: params.slug },
      status: { equals: 'published' },
    },
    depth: 2,
    limit: 1,
  })

  const post = docs[0]
  if (!post) notFound()

  const author = typeof post.author === 'object' ? post.author : null
  const categories = post.categories?.filter((c) => typeof c === 'object') ?? []

  return (
    <main className="container mx-auto max-w-3xl px-4 py-12">
      {/* カテゴリ */}
      <div className="mb-4 flex flex-wrap gap-2">
        {categories.map((cat: any) => (
          <Badge key={cat.id} variant="secondary">
            {cat.name}
          </Badge>
        ))}
      </div>

      {/* タイトル */}
      <h1 className="mb-4 text-4xl font-bold tracking-tight">{post.title}</h1>

      {/* メタ情報 */}
      <div className="mb-6 flex items-center gap-4 text-sm text-muted-foreground">
        {author && <span>著者: {author.name}</span>}
        {post.publishedAt && (
          <span>
            {new Date(post.publishedAt).toLocaleDateString('ja-JP', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </span>
        )}
      </div>

      <Separator className="mb-8" />

      {/* 本文（リッチテキスト） */}
      <article className="prose prose-slate max-w-none">
        {/* Payload の RichText レンダリングは別途 RichTextComponent を実装 */}
        <pre className="whitespace-pre-wrap text-sm">
          {JSON.stringify(post.content, null, 2)}
        </pre>
      </article>

      <Separator className="my-8" />

      <Link href="/blog" className="text-sm text-muted-foreground hover:underline">
        ← 記事一覧に戻る
      </Link>
    </main>
  )
}
```

> **補足:** リッチテキストのレンダリングには `@payloadcms/richtext-lexical` が提供する `RichText` コンポーネントを使用することを推奨します。詳細は[公式ドキュメント](https://payloadcms.com/docs/rich-text/overview)を参照してください。

### 7-4. フロントエンド用レイアウト

```tsx
// src/app/(frontend)/layout.tsx
import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'My Blog',
  description: 'Payload CMS で作るブログ',
}

export default function FrontendLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <header className="border-b">
          <div className="container mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
            <Link href="/" className="text-xl font-bold">
              My Blog
            </Link>
            <nav>
              <Link href="/blog" className="text-sm hover:underline">
                記事一覧
              </Link>
            </nav>
          </div>
        </header>
        {children}
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

---

## 8. 動作確認

### 8-1. 依存パッケージのインストール

```bash
pnpm install
```

### 8-2. DB マイグレーションの実行

```bash
pnpm payload migrate
```

### 8-3. 開発サーバーの起動

```bash
pnpm dev
```

### 8-4. 管理画面へアクセスして初期ユーザー登録

1. ブラウザで `http://localhost:3000/admin` を開く
2. 「Create your first user」画面で管理者ユーザーを登録
3. ログイン後、管理画面から記事・カテゴリを作成

### 8-5. フロントエンドの確認

| URL | 内容 |
|-----|------|
| `http://localhost:3000/admin` | Payload 管理画面 |
| `http://localhost:3000/blog` | 記事一覧ページ |
| `http://localhost:3000/blog/[slug]` | 記事詳細ページ |

---

## 9. ディレクトリ構成（最終）

```
my-blog/
├── public/
│   └── media/                    # アップロード画像の保存先
├── src/
│   ├── app/
│   │   ├── (frontend)/           # フロントエンド（公開側）
│   │   │   ├── blog/
│   │   │   │   ├── page.tsx      # 記事一覧
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx  # 記事詳細
│   │   │   ├── globals.css
│   │   │   └── layout.tsx
│   │   └── (payload)/            # Payload 管理画面
│   │       └── admin/
│   ├── collections/
│   │   ├── Users.ts
│   │   ├── Posts.ts
│   │   ├── Categories.ts
│   │   └── Media.ts
│   ├── components/
│   │   └── ui/                   # shadcn/ui コンポーネント
│   ├── lib/
│   │   └── payload.ts            # Payload クライアントユーティリティ
│   ├── payload.config.ts         # Payload 設定
│   └── payload-types.ts          # 自動生成される型定義
├── .env
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## よくある問題と対処法

### `DATABASE_URI` 接続エラー

- PostgreSQL が起動しているか確認: `pg_ctl status`
- `.env` のユーザー名・パスワード・DB名が正しいか再確認

### 型定義が見つからないエラー

```bash
pnpm payload generate:types
```

### マイグレーションのリセット

開発中にスキーマを変更した場合:

```bash
pnpm payload migrate:fresh
```

> **⚠️ 注意:** `migrate:fresh` はデータを全削除します。本番環境では使用しないでください。

---

*作成日: 2025年*  
*バージョン: Payload 3.x / Next.js 15.x*
