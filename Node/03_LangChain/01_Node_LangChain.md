# Next.jsでLangChainを実装する方法

- NodeでのLangChainの実装例

## 関連のモジュールをインストール

```sh
npm install @langchain/google-genai @langchain/core langchain
```

## 環境変数の設定

- .env

```sh
GOOGLE_AI_ST_API=your_google_api_key_here
```

## API Routeの実装

- src/app/api/code-review/route.ts

```ts
import { NextRequest, NextResponse } from "next/server";
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

// モデルの初期化
const model = new ChatGoogleGenerativeAI({
  model: "gemini-2.5-flash",
  apiKey: process.env.GOOGLE_AI_ST_API,
  temperature: 0,
});

// プロンプトの定義
const prompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    `あなたは熟練のシニアエンジニアです。
ユーザがレビュー依頼があったコードに対してレビューを行い。以下のフォーマットでレポートを返してください。
## フォーマット
正確性スコア：（得点）/10<br/>
可読性スコア：（得点）/10<br/>
安全性スコア：（得点）/10<br/>
【詳細なコードレビューのフィードバック】<br/>

（フィードバックの内容）

【修正案】<br/>

（修正する内容）`,
  ],
  ["human", "以下のコードをレビューしてください:\n{source_code}"],
]);

// チェーンの定義
const chain = prompt.pipe(model).pipe(new StringOutputParser());

export async function POST(req: NextRequest) {
  try {
    const { sourceCode } = await req.json();

    if (!sourceCode) {
      return NextResponse.json(
        { error: "sourceCode is required" },
        { status: 400 }
      );
    }

    const result = await chain.invoke({ source_code: sourceCode });

    return NextResponse.json({ result });
  } catch (error) {
    console.error("Review error:", error);
    return NextResponse.json(
      { error: "Failed to review code" },
      { status: 500 }
    );
  }
}
```

## フロント画面の実装

- src/app/page.tsx

```tsx
"use client";

import { useState } from "react";

export default function CodeReviewPage() {
  const [sourceCode, setSourceCode] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleReview = async () => {
    if (!sourceCode.trim()) return;
    setLoading(true);
    setResult("");

    try {
      const res = await fetch("/api/code-review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sourceCode }),
      });

      const data = await res.json();
      setResult(data.result ?? data.error);
    } catch (e) {
      setResult("エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <h1>コードレビューエージェント</h1>

      <textarea
        value={sourceCode}
        onChange={(e) => setSourceCode(e.target.value)}
        placeholder="レビューするコードをここに貼り付けてください..."
        rows={15}
        style={{ width: "100%", fontFamily: "monospace", padding: "1rem" }}
      />

      <button
        onClick={handleReview}
        disabled={loading}
        style={{ marginTop: "1rem", padding: "0.75rem 2rem" }}
      >
        {loading ? "レビュー中..." : "レビュー実行"}
      </button>

      {result && (
        <div
          style={{
            marginTop: "2rem",
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            whiteSpace: "pre-wrap",
          }}
        >
          <h2>レビュー結果</h2>
          <div dangerouslySetInnerHTML={{ __html: result }} />
        </div>
      )}
    </div>
  );
}
```

## 実装例

![実装例](https://i.gyazo.com/92510143ac83f8f055a179ab67d2f86c.gif)


## 【備考】Pythonコードとの対応関係

| Python | Node/Next.js |
|---|---|
| `ChatGoogleGenerativeAI` | `@langchain/google-genai` の同名クラス |
| `ChatPromptTemplate.from_messages()` | `ChatPromptTemplate.fromMessages()` |
| `StrOutputParser()` | `StringOutputParser()` |
| `chain.invoke()` | `await chain.invoke()` (非同期) |
| `TextLoader` | API経由でフロントから直接送信 |
| ファイル出力 | JSONレスポンスとして返却 |