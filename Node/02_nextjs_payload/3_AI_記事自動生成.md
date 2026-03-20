# AI記事自動生成

- LangChainを使用して記事の自動生成を実装

## 関連のモジュールをインストール

```sh
npm install @langchain/google-genai @langchain/core langchain
```

## 記事生成 API Route の作成

- src\app\api\generate-content\route.ts

```ts
import { NextRequest, NextResponse } from 'next/server'
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { ChatPromptTemplate } from '@langchain/core/prompts'

export async function POST(req: NextRequest) {
  const { title } = await req.json()

  if (!title) {
    return NextResponse.json({ error: 'タイトルが必要です' }, { status: 400 })
  }

  const model = new ChatGoogleGenerativeAI({
    model: "gemini-2.5-flash",
    apiKey: process.env.GOOGLE_AI_ST_API,
    temperature: 0.7,
  });

  const prompt = ChatPromptTemplate.fromMessages([
    [
      'system',
      `あなたはブログ記事を書くプロのライターです。
       与えられたタイトルに基づいて、SEOを意識した読みやすいブログ記事を日本語で書いてください。
       構成：導入文 → 本文（見出し2〜3つ） → まとめ`,
    ],
    ['human', 'タイトル: {title}'],
  ])

  const chain = prompt.pipe(model)
  const response = await chain.invoke({ title })

  return NextResponse.json({
    content: response.content,
  })
}
```

## AI 生成ボタンのカスタムコンポーネント作成

- src\components\admin\AIGenerateButton\index.tsx

```tsx
'use client'

import { useField, useFormFields } from '@payloadcms/ui'
import { useState } from 'react'

export function AIGenerateButton() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [generatedContent, setGeneratedContent] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const titleField = useFormFields(([fields]) => fields['title'])
  const title = titleField?.value as string

  const { setValue: setExcerpt } = useField({ path: 'excerpt' })
  
  const handleGenerate = async () => {
    if (!title) {
      setError('先にタイトルを入力してください')
      return
    }

    setLoading(true)
    setError(null)
    setGeneratedContent(null)

    try {
      const res = await fetch('/api/generate-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      })

      if (!res.ok) throw new Error('生成に失敗しました')
      
      const { content } = await res.json()
      const firstSentence = content.split('\n').find((s: string) => s.trim()) ?? ''
      setExcerpt(firstSentence)
      setGeneratedContent(content)
    } catch (e) {
      setError('記事の生成に失敗しました。もう一度お試しください。')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (!generatedContent) return
    await navigator.clipboard.writeText(generatedContent)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      {/* 生成ボタン */}
      <button
        type="button"
        onClick={handleGenerate}
        disabled={loading || !title}
        style={{
          padding: '8px 16px',
          backgroundColor: loading || !title ? '#ccc' : '#6d5dfc',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading || !title ? 'not-allowed' : 'pointer',
          fontWeight: 'bold',
        }}
      >
        {loading ? '生成中...' : '✨ AIで記事を自動生成'}
      </button>

      {!title && (
        <p style={{ color: '#888', fontSize: '12px', marginTop: '4px' }}>
          タイトルを入力すると生成できます
        </p>
      )}

      {error && (
        <p style={{ color: 'red', fontSize: '12px', marginTop: '4px' }}>{error}</p>
      )}

      {/* 生成結果プレビューエリア */}
      {generatedContent && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '4px',
          }}>
            <p style={{ margin: 0, fontSize: '13px', fontWeight: 'bold' }}>
              生成結果（下のエディタにコピペしてください）
            </p>
            {/* コピーボタン */}
            <button
              type="button"
              onClick={handleCopy}
              style={{
                padding: '4px 12px',
                backgroundColor: copied ? '#22c55e' : '#e2e8f0',
                color: copied ? 'white' : '#333',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              {copied ? '✓ コピーしました' : 'クリップボードにコピー'}
            </button>
          </div>

          {/* テキスト表示エリア */}
          <textarea
            readOnly
            value={generatedContent}
            rows={15}
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '13px',
              lineHeight: '1.7',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              backgroundColor: '#f9fafb',
              resize: 'vertical',
              fontFamily: 'inherit',
              boxSizing: 'border-box',
            }}
          />
        </div>
      )}
    </div>
  )
}
```

## Posts コレクションに UI Field として追加

- 【追加修正】
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
      name: 'aiGenerate',
      type: 'ui',
      admin: {
        components: {
          Field: '@/components/admin/AIGenerateButton#AIGenerateButton',
        },
      },
    },
    {省略}
  ]
}
```

## 環境変数の追加

- .env

```sh
GOOGLE_AI_ST_API=xxxxxxxxxxxxxxxxxx
```

## パスの修正

```sh
npx payload generate:importmap
```

## サンプル動画

- 記事生成例

[![サンプル動画1](https://i.gyazo.com/372f72208895016ca0a379582f2d8e6c.gif)](https://gyazo.com/372f72208895016ca0a379582f2d8e6c)

- フロント画面例

[![サンプル動画2](https://i.gyazo.com/c420493bd1a51fd9124dec8573fcf0a3.gif)](https://gyazo.com/c420493bd1a51fd9124dec8573fcf0a3)