# ローカルLLMでデザイン系SKILLSを読み込んでHTMLファイルを生成

- Ollama・ローカルLLM(gemma4:e4b)を使用
- デザイン系SKILL(frontend-design)を読み込み、ローカルLLM(gemma4:e4b)に学習させた上でHTMLファイルを生成

[frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)

# 実装内容

- [共通関数](./実装source/common.py)
- [SKILLファイル読み込みのみの実装ソース](./実装source/cleate_html01.py)
- [SKILLファイル+設計書読み込み実装ソース](./実装source/cleate_html02.py)

## 1.SKILLS読み込み

```py
## SKILLのパスと出力先パス
SKILL_PATH    = "./skills/frontend-design.md"
skill_text = Path(SKILL_PATH).read_text(encoding="utf-8")
```

## 2.入力トークン量の確認

- ローカル環境PCのスペックと使用モデルで`最大のコンテキストウィンドウ`を算出
- 入力するコンテキストウィンドウが`最大のコンテキストウィンドウ`で足りるのか確認

```py
# 一度に読み書きできるコンテキストウィンドウ
CONTEXT_NUM = 16384
## トークン量の確認
SKILL_PATH    = "./skills/frontend-design.md"
skill_text = Path(SKILL_PATH).read_text(encoding="utf-8")
# SKILLを除いた固定部分だけのトークン数
fixed_system = """You are an expert frontend engineer.

## Design Guidelines

## Output Rules
- Output ONLY the complete HTML source code.
- Include all CSS inside <style> tags in <head>.
- Include all JavaScript inside <script> tags before </body>.
- No JSON wrapping, no markdown fences, no explanation.
- Output starts with <!DOCTYPE html> and ends with </html>.
"""
overhead_tokens = len(fixed_system) / 3
skill_tokens  = len(skill_text) / 3   # 英語: 約3文字/token
system_tokens = skill_tokens + overhead_tokens # system prompt
total = skill_tokens + system_tokens
rest_context = CONTEXT_NUM - total
print(f"SKILL   : {skill_tokens:.0f} tokens")
print(f"合計(入力): {total:.0f} tokens")
print(f"残り(出力用): {rest_context:.0f} tokens")
```

## 3.プロンプトとChainを作成
```py
## ollama用callbackを読み込む
ollama_callback = OllamaMetadataCallback()
## モデル設定
gemma_model = ChatOllama(
  model="gemma4:e4b",
  base_url=os.environ['OLLAM_URL'],
  temperature=0.7,
  num_ctx=CONTEXT_NUM,
  extra_body={"think": False},
  callbacks=[ollama_callback]
)
## プロンプト作成
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert frontend engineer.

## Design Guidelines
{skill_text}

## Output Rules
- Output ONLY the complete HTML source code.
- Include all CSS inside <style> tags in <head>.
- Include all JavaScript inside <script> tags before </body>.
- No JSON wrapping, no markdown fences, no explanation.
- Output starts with <!DOCTYPE html> and ends with </html>.
"""),
    ("human", "{request}")
])
## chain作成
chain = (
  {
    "skill_text": RunnableLambda(lambda _: skill_text),  # 固定値を注入
    "request": RunnablePassthrough()
  }
  | prompt
  | gemma_model
  | StrOutputParser()
)
```

## 4.実行

> SKIILSのみの場合

- 出力先のパスを指定(例:out01)

```py
## 出力先パス
OUTPUT_DIR    = "out01"
request="自然感がありリッチ感があるホテルのトップページを作成してください。また、画像を使わない条件で作成してください。"
if (rest_context > 0):
  try:
    res = chain.invoke(request)
    ## 生成されたものからHTMLファイルに変換
    html_file = extract_html(res)
    save_files(html_file, OUTPUT_DIR)
    # 最低限のバリデーション
    assert "<body" in html_file.lower(), "bodyタグがありません"
    assert "<style" in html_file.lower() or "style=" in html_file.lower(), "CSSがありません"
    # HTMLファイルからHTML・CSS・JSファイルに分割
    split_html_to_files(html_file, OUTPUT_DIR)
  except (json.JSONDecodeError, ValueError, AssertionError) as e:
    print(f"⚠️  エラー: {e}")
  ## callback出力
  cb_summary = ollama_callback.summary()
  common.res_output_md(cb_summary,dir_str=OUTPUT_DIR,file_name="callback-summary")
else:
  print(f'''⚠️  エラー: コンテキストウィンドが足りません
        コンテキストウィンドを調整してください。''')
```

> SKIILS + 簡単なプロンプトを追加する場合

- 出力先のパスを指定(例:out02)

```py
## 出力先パス
OUTPUT_DIR    = "out02"
request = """
自然感がありリッチ感があるホテルのトップページを作成してください。
画像は使用しないこと。

## デザイン要件
- カラーパレット：アイボリー (#FAF7F2)、ディープグリーン (#1C3A2A)、ゴールド (#C9A96E) の3色を基調
- ヒーローセクション：CSS linear-gradientで深い森をイメージした背景、中央に大きなキャッチコピー
- フォント：見出しはセリフ体（Playfair Display）、本文はサンセリフ（Inter）
- アニメーション：スクロール時のfadeIn、ホバー時のtransition
- セクション構成：
  1. フルスクリーンヒーロー（gradient背景 + キャッチコピー + CTAボタン）
  2. 3カラムの体験紹介（アイコン代わりにUnicode絵文字可）
  3. 客室紹介（カード形式、ホバーで影が出る）
  4. フッター（ダークグリーン背景）
- ヒーローの背景はlinear-gradient(135deg, #0a1f13 0%, #1C3A2A 50%, #2d5a3d 100%)
- 全体的に余白を広く取り、高級感を演出
- CSSアニメーション（@keyframes fadeInUp）をスクロール要素に適用
"""
if (rest_context > 0):
  try:
    res = chain.invoke(request)
    ## 生成されたものからHTMLファイルに変換
    html_file = extract_html(res)
    save_files(html_file, OUTPUT_DIR)
    # 最低限のバリデーション
    assert "<body" in html_file.lower(), "bodyタグがありません"
    assert "<style" in html_file.lower() or "style=" in html_file.lower(), "CSSがありません"
    # HTMLファイルからHTML・CSS・JSファイルに分割
    split_html_to_files(html_file, OUTPUT_DIR)
  except (json.JSONDecodeError, ValueError, AssertionError) as e:
    print(f"⚠️  エラー: {e}")
  ## callback出力
  cb_summary = ollama_callback.summary()
  common.res_output_md(cb_summary,dir_str=OUTPUT_DIR,file_name="callback-summary")
else:
  print(f'''⚠️  エラー: コンテキストウィンドが足りません
        コンテキストウィンドを調整してください。''')
```

> SKIILS + 設計書を追加する場合

- 出力先のパスを指定(例:out03)

```py
## 出力先パス
OUTPUT_DIR    = "out03"
## 設計書読み込み
DOC_PATH  = "./docs/desing_doc.md"
## 設計書の量が多い為圧縮
exclude_sections = [
  "## 1. プロジェクト概要",
  "## 6. アクセシビリティ"
]
doc_text = extract_key_sections(
  Path(DOC_PATH).read_text(encoding="utf-8"),
  exclude=exclude_sections
)
request = f"""
以下の設計書に従い、ホテルのトップページを1つのHTMLファイルとして作成してください。
画像は一切使用せず、CSSのみで視覚表現してください。

## 設計書
{doc_text}

## 追加指示：CSS絵の実装（必須）
客室カードのプレースホルダー divは使用禁止。

"""
if (rest_context > 0):
  try:
    res = chain.invoke(request)
    ## 生成されたものからHTMLファイルに変換
    html_file = extract_html(res)
    save_files(html_file, OUTPUT_DIR)
    # 最低限のバリデーション
    assert "<body" in html_file.lower(), "bodyタグがありません"
    assert "<style" in html_file.lower() or "style=" in html_file.lower(), "CSSがありません"
    # HTMLファイルからHTML・CSS・JSファイルに分割
    split_html_to_files(html_file, OUTPUT_DIR)
  except (json.JSONDecodeError, ValueError, AssertionError) as e:
    print(f"⚠️  エラー: {e}")
  ## callback出力
  cb_summary = ollama_callback.summary()
  common.res_output_md(cb_summary,dir_str=OUTPUT_DIR,file_name="callback-summary")
else:
  print(f'''⚠️  エラー: コンテキストウィンドが足りません
        コンテキストウィンドを調整してください。''')
```

## 5.出力内容

> SKIILなしの場合

- [HTMLファイル](./出力内容/out_noskill/index.html)
- [CSSファイル](./出力内容/out_noskill/style.css)
- [JSファイル](./出力内容/out_noskill/app.js)

![SKIILなし](https://i.gyazo.com/269a9ccab89828cba4dbd68c74ce7940.gif)

|モデル|処理時間(分)|入力token|出力token|料金ベースモデル|コスト(円)|
|:----|:----|:----|:----|:----|:----|
|gemma4:e4b|2.32|118|5,605|gemini-2.5-flash|2.27|


> SKIILSのみの場合

- [HTMLファイル](./出力内容/out01/index.html)
- [CSSファイル](./出力内容/out01/style.css)

![SKIILSのみ](https://i.gyazo.com/bd1cf0d0443e682c460eacf4225fc4cd.gif)

|モデル|処理時間(分)|入力token|出力token|料金ベースモデル|コスト(円)|
|:----|:----|:----|:----|:----|:----|
|gemma4:e4b|1.84|1,839|4,637|gemini-2.5-flash|1.96|


> SKIILS + 簡単なプロンプトを追加する場合

- [HTMLファイル](./出力内容/out02/index.html)
- [CSSファイル](./出力内容/out02/style.css)
- [JSファイル](./出力内容/out02/app.js)

![SKIILS + 簡単なプロンプト](https://i.gyazo.com/86db80f4f6bde959db03343028364563.gif)


|モデル|処理時間(分)|入力token|出力token|料金ベースモデル|コスト(円)|
|:----|:----|:----|:----|:----|:----|
|gemma4:e4b|2.50|2,099|5,628|gemini-2.5-flash|2.38|


> SKIILS + 設計書を追加する場合

- [HTMLファイル](./出力内容/out03/index.html)
- [CSSファイル](./出力内容/out03/style.css)
- [JSファイル](./出力内容/out03/app.js)

![SKIILS + 設計書](https://i.gyazo.com/ec0036978439669a258afeafa061ee10.gif)

|モデル|処理時間(分)|入力token|出力token|料金ベースモデル|コスト(円)|
|:----|:----|:----|:----|:----|:----|
|gemma4:e4b|5.71|3,876|11,955|gemini-2.5-flash|5.02|
