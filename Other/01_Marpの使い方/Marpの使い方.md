# Marpについて-スライド作成方法-

## 0. 概要

MarpはMarkdown（マークダウン）形式で記述したテキストから、プレゼンテーションスライドを作成できる無料のオープンソースツールです。

https://marp.app/

https://marpit.marp.app/

また基本的な使用方法とAIモデルを使用した生成方法について紹介します。

## 1. Marpの特徴

- Markdown（マークダウン）形式で記述したテキストから、プレゼンテーションスライドを作成できます。
- 組み込みテーマやCSSをあてることでスライドのデザインを整える事が可能です。
- Markdownの画像構文の拡張によりスライドに差し込むことや背景にすることが可能です。
- 出力方法もpdf、htmlおよびpowerPoint（※LibreOfficeのインストール必要）などの出力ができます。

## 2. VSCode拡張機能

MarpはVSCodeの拡張機能を用意しており、Markdownを編集しながらスライドの出力プレビューで確認が出来ます。

https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode


## 3. 基本的な使い方

> ファイル配置例

```sh
.project
├───img
│    ├──sample01.png
│    └──sample02.png
└──sample.md
```

下記のsample.mdを参考にMarkDowon記法で記述します。

[sample.md](./テンプレート/sample.md)

編集もしくは作成後、「プレビュー」画面で内容が確認できます。

> 出力例

- PDF

[slide.pdf](./テンプレート/出力/slide.pdf)

- html

[slide.html](./テンプレート/出力/slide.html)

## 4. ClaudeCodeでの出力方法

> ファイル配置例

```sh
.project
├───doc
│    └──headless_cms.md
├───出力
└── CLAUDE.md　(※CLAUDE.mdに関しては触れません)
```

上記の様に配置した後に下記の様にプロントをmodelに投げます。

```sh
「 docs/headless_cms.md 」を読んで、「出力/」配下にMarp形式のスライド（claudeCodeSlide.md）に変換して作成してください。
「theme」・「size」・「paginate」・「style」は下記を適応してください。
\```md
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
\```
今回はソースコードの作成は不要です。スライド（slides.md）のみ作成し、「出力/」配下に設置してください。
```

> 出力例

- Markdownファイル(Marp)

[headless_cms_slides.md](./出力/headless_cms_slides.md)


## 5. ローカルLLMでの出力方法

ローカルLLMでMarp形式のスライドを作成する事も可能となります。
また、セクションごとに分けて最後に結合させる仕組みを入れることで、軽量のローカルLLMでも出力可能になります。

> 技術概要

- NVIDIA GeForce RTX 4060 Laptop
- 標準メモリ構成: 8 GB
- モデル：gemma4:e4b
- Python
- Ollama
- LangChain/LangGraph


> ファイル配置例

```sh
.project
├───doc
│    └── headless_cms.md
└── marap.py
```

出力ソースは下記を参考に「py marap.py "headless_cms.md"」を実行する事でMarp形式のスライドを作成ができます。

[marap.py](./python_source/marap.py)

## 6. おススメツール

MarkdownおよびMarp形式のスライドを作成する際に便利なツールを紹介します。

> テーブルを作成するツール

[Markdown表変換ツール](https://boost-tool.com/ja/tools/md_table)

> 図形などを描画する際のツール

[Draw.io](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)

## 7. さいごに
- Marpを使うことで1つのエディター画面(VSCode)で資料を見ながら作成する事が可能となるので作業効率が上がると思います
- 設計書やドキュメントを作成し、スライドは生成AIに作成を依頼する事でスライド作成の手間が減ると思います

## 【参考】

- [Markdown でスライドを作れる Marp はいいぞ](https://qiita.com/tomoasleep/items/604107787d92dec4868e)
- [【VS Code + Marp】Markdownから爆速・自由自在なデザインで、プレゼンスライドを作る](https://qiita.com/tomo_makes/items/aafae4021986553ae1d8)
- [Marpで作成したスライドをPDF出力する](https://qiita.com/firesign2023/items/bc20bc751cf43b66eb4c)
- [Marp for VSCodeを使った編集可能なPowerPointの入門](https://qiita.com/bakucat/items/ab153b4e24ea8316ce74)