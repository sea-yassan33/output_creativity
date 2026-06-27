# ClaudeCode_desing概要

- ClaudeCode_CLIにてSKILLSを使用してフロント画面を実装
- SKILLSはfrontend-design@claude-code-pluginsを使用

## 1.CLAUDE.md作成

- [CLAUDE.md](./CLAUDE.md)

## 2.claude_code接続

- 下記のコマンドで基本設定を行う

```sh
## アクセス
claude

## モデル確認
/model

## Effort Level（思考の深さ）の調整
/effort
```

## 3.frontend-design@claude-code-plugins導入

- マーケットプレイスのプラグインを入れていない場合は導入
- frontend-design@claude-code-pluginsを導入

```sh
## マーケットプレイスを追加してない場合は実施
/plugin marketplace add anthropics/claude-code

## frontend-design@claude-code-plugins導入
/plugin install frontend-design@claude-code-plugins

❯ /plugin install frontend-design@claude-code-plugins
     Install for you (user scope)
   > Install for all collaborators on this repository (project scope)
     Install for you, in this repo only (local scope)
     Back to plugin list
  ⎿  ✓ Installed frontend-design. Run /reload-plugins to apply.

## 導入されたか確認
/plugin list
```

## 4.SKILLSを指定して実行

- モデル：Sonnet 4.6
- 思考の深さ：低

```sh
/frontend-design:frontend-design 自然感がありリッチ感があるホテルのトップページを作成してください。また、画像を使わない条件で作成してください。./src/dev260627/配下にhtml,css,js形式で作成してください。
```

## 5.出力内容

実行時間：約5分程

```sh
./projct
├── CLAUDE.md
├── docs/ # 設計書
│   ├──dev260627
│   │   └──design-spec.md 
│   └──
├── src/  # ソースコード
│   ├──dev260627
│   │   ├──index.html
│   │   ├──main.js
│   │   └──style.css
│   └──
├── _bk{YYMMDD}/ # 不要ファイルの退避先
│ 
└── project-tokens.py # トークン量取得用
``` 

- [HTMLファイル](./dev260627/index.html)
- [CSSファイル](./dev260627/style.css)
- [jsファイル](./dev260627/main.js)


![フロント画面](https://i.gyazo.com/7b77292fc43ea06447f8ec05bc29133e.gif)


## 6.実行時のトークン量(目安)

>[モデル毎の値段](https://platform.claude.com/docs/en/about-claude/pricing)

|model|input_tokens|output_tokens|cache_creation_input_tokens|cache_read_input_tokens|
|:----|:----|:----|:----|:----|
|Sonnet 4.6|9|19,757|30,454|271,836|

|コスト||
|:----|:----|
|0.49ドル|79円|