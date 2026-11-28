# next_js開発環境　【2026年版】

2026年11月時点、各パッケージをlatestでインストールした際のバージョン

|             | version |
| ----------- | ------- |
| Next.js     | 16.4.6  |
| typescript  | 5系     |
| tailwindcss | 4.3.3   |
| tailwind-animations | 1系   |
| shadcn      | 4.23.1   |

## 1.nodeバージョンの確認

```sh
node -v

npm -v

npx -v

npm install -g yarn

yarn -v
```

## 2.Next.jsプロジェクト作成

```sh
npx create-next-app@latest

Need to install the following packages:
create-next-app@16.4.6

√ What is your project named? ... {プロジェクト名}
√ Would you like to use the recommended Next.js defaults? » No, customize settings　
√ Would you like to use TypeScript? ... Yes
√ Which linter would you like to use? » ESLint
√ Would you like to use React Compiler? ... Yes
√ Would you like to use Tailwind CSS? ... Yes
√ Would you like your code inside a `src/` directory? ... Yes
√ Would you like to use App Router? (recommended) ... Yes
√ Would you like to use Cache Components? ... Yes
√ Would you like to customize the import alias (`@/*` by default)? ... No
√ Would you like to include AGENTS.md to guide coding agents to write up-to-date Next.js code? ... No
√ Would you like to help improve Next.js by letting agents prepare anonymized feedback for your review as you code? (Disable anytime with `experimental.agentFeedback: false`.) ... No
```

## 3.UIやアニメーション実装に必要なパッケージをインストール

```sh
## tailwind-css animations
npm install tailwind-animations

## ui.shadcn
npx shadcn@latest init -d
npx shadcn@latest add button
```

## 4.src\app\globals.cssの確認

`src\app\globals.css`に「tailwind-css animations」や「shadcn」が適応されているか確認

```css
@import "tailwindcss";
@import 'tailwind-animations';
@import "tw-animate-css";
@import "shadcn/tailwind.css";
```

## 5.コンポーネント作成

- src\components\home\HomeComponet.tsx

```tsx
"use client";

import { useState } from "react";
import { Loader2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

const variants = [
  "default",
  "secondary",
  "destructive",
  "outline",
  "ghost",
  "link",
] as const;
const sizes = ["sm", "default", "lg"] as const;
const animations = [
  "animate-fade-in",
  "animate-fade-in-up",
  "animate-zoom-in",
  "animate-bounce-in",
  "animate-slide-in-left",
  "animate-slide-in-right",
  "animate-flip-in-x",
  "animate-wiggle",
  "animate-jiggle",
  "animate-shake",
  "animate-tada",
  "animate-heartbeat",
] as const;

export default function HomeComponent() {
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(false);
  // key を変えて再マウントし、アニメーションを再生し直す
  const [replayKey, setReplayKey] = useState(0);
  const handleLoading = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1500);
  };

  return (
    <main className="mx-auto max-w-4xl space-y-12 p-8">
      <header className="animate-fade-in-down space-y-2">
        <h1 className="text-3xl font-bold">インストール確認ページ</h1>
        <p className="text-muted-foreground">
          見出しがフェードインし、ボタンにスタイルが当たっていれば正常です。
        </p>
      </header>
      {/* ===== shadcn/ui Button ===== */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">1. shadcn/ui Button</h2>
        <div className="space-y-6 rounded-lg border p-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">variant</p>
            <div className="flex flex-wrap gap-2">
              {variants.map((v) => (
                <Button key={v} variant={v}>
                  {v}
                </Button>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">size</p>
            <div className="flex flex-wrap items-center gap-2">
              {sizes.map((s) => (
                <Button key={s} size={s}>
                  {s}
                </Button>
              ))}
              <Button size="icon" aria-label="追加">
                <Plus />
              </Button>
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">動作</p>
            <div className="flex flex-wrap items-center gap-2">
              <Button onClick={() => setCount((c) => c + 1)}>
                クリック回数: {count}
              </Button>
              <Button
                variant="outline"
                onClick={handleLoading}
                disabled={loading}
              >
                {loading && <Loader2 className="animate-spin" />}
                {loading ? "処理中..." : "ローディング"}
              </Button>
              <Button disabled>disabled</Button>
            </div>
          </div>
        </div>
      </section>
      {/* ===== tailwind-animations ===== */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">2. tailwind-animations</h2>
        <p className="text-muted-foreground">
          アニメーションを再生ボタンを押下しアニメーションが機能しれいれば正常
        </p>
        <div className="space-y-6 rounded-lg border p-6">
          <Button variant="outline" onClick={() => setReplayKey((k) => k + 1)}>
            アニメーションを再生
          </Button>
          <div
            key={replayKey}
            className="grid grid-cols-2 gap-4 sm:grid-cols-3"
          >
            {animations.map((cls) => (
              <div
                key={cls}
                className={`${cls} flex h-20 items-center justify-center rounded-md bg-primary px-2 text-center font-mono text-xs text-primary-foreground`}
              >
                {cls.replace("animate-", "")}
              </div>
            ))}
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">
              delay / duration / iteration-count
            </p>
            <div key={`mod-${replayKey}`} className="flex flex-wrap gap-4">
              <div className="animate-fade-in animate-delay-500 rounded-md bg-secondary px-4 py-2 text-sm">
                delay-500
              </div>
              <div className="animate-fade-in animate-delay-1000 rounded-md bg-secondary px-4 py-2 text-sm">
                delay-1000
              </div>
              <div className="animate-zoom-in animate-duration-slow rounded-md bg-secondary px-4 py-2 text-sm">
                duration-slow
              </div>
              <div className="animate-wiggle animate-iteration-count-infinite rounded-md bg-secondary px-4 py-2 text-sm">
                infinite
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
```

## 6.page.tsxを編集

- src\app\page.tsx

```tsx
import HomeComponent from "@/components/home/HomeComponet";

export default function Home() {
  return (
    <main>
      <HomeComponent />
    </main>
  );
}
```

## 7.フロント画面確認

下記のコマンドでNext.jsを起動します。

```sh
npm run dev
```

下記にアクセスして確認します。

```text
http://localhost:3000
```

## その他

> VScode拡張機能について

https://marketplace.visualstudio.com/items?itemName=xabikos.JavaScriptSnippets

https://marketplace.visualstudio.com/items?itemName=formulahendry.auto-close-tag

https://marketplace.visualstudio.com/items?itemName=formulahendry.auto-rename-tag

https://marketplace.visualstudio.com/items?itemName=dsznajder.es7-react-js-snippets

https://marketplace.visualstudio.com/items?itemName=yoavbls.pretty-ts-errors

https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss

https://marketplace.visualstudio.com/items?itemName=PulkitGangwar.nextjs-snippets

> Vscodeのsettings.jsonに追加

```json
{
  "tailwindCSS.experimental.classRegex": [
    ["tv\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

## 公式ドキュメント

> Next.js

https://nextjs.org/docs/app/getting-started/installation

> tailwind-animasions

https://tailwind-animations.com

> shadcn

https://ui.shadcn.com/docs/installation