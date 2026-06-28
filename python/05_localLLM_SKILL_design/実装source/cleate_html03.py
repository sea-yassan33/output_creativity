import warnings
# 警告を非表示にする
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True
import os
from dotenv import load_dotenv
load_dotenv()
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re
# Langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from langchain_core.output_parsers import StrOutputParser
# 共通関数
import common
from common import GoogleMetadataCallback
# ───────────────────────────────
# 関数
# ───────────────────────────────
def format_docs(docs):
  return "\n\n---\n\n".join(d.page_content for d in docs)
def extract_key_sections(
  md_text: str,
  exclude: list[str],
  heading_level: str = "## "
) -> str:
  """実装不要なセクションを除外"""
  lines = md_text.split("\n")
  result, skip = [], False
  for line in lines:
    if any(line.startswith(ex) for ex in exclude):
      skip = True
    elif line.startswith(heading_level) and skip:
      skip = False
    if not skip:
      result.append(line)
  return "\n".join(result)
def extract_html(text: str) -> str:
  """モデル出力から生HTMLを堅牢に抽出する"""
  # Thinkingタグを除去
  text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
  # マークダウンのコードブロックを除去
  text = re.sub(r"```html|```", "", text).strip()
  # <!DOCTYPE html> から </html> を抽出
  start = text.lower().find("<!doctype html")
  if start == -1:
    start = text.lower().find("<html")
  end = text.lower().rfind("</html>") + len("</html>")
  if start == -1 or end < len("</html>"):
    raise ValueError(f"HTMLが見つかりませんでした。出力先頭:\n{text[:300]}")
  return text[start:end]
def save_files(html: str, output_dir: str):
  """HTMLを保存"""
  out = Path(output_dir)
  out.mkdir(parents=True, exist_ok=True)
  (out / "index00.html").write_text(html, encoding="utf-8")
def split_html_to_files(html: str, output_dir: str):
  """単一HTMLからCSS・JSを抽出して3ファイルに分割して保存する"""
  out = Path(output_dir)
  out.mkdir(parents=True, exist_ok=True)
  soup = BeautifulSoup(html, "html.parser")
  # --- CSS抽出 ---
  css_blocks = []
  for tag in soup.find_all("style"):
    css_blocks.append(tag.get_text())
    tag.decompose()
  # --- JS抽出 ---
  js_blocks = []
  for tag in soup.find_all("script"):
    # src属性がある外部スクリプト（CDNなど）は除外
    if not tag.get("src"):
      js_blocks.append(tag.get_text())
      tag.decompose()
  # --- HTMLに外部ファイルへのリンクを挿入 ---
  if css_blocks and soup.head:
    link_tag = soup.new_tag("link", rel="stylesheet", href="style.css")
    soup.head.append(link_tag)
  if js_blocks and soup.body:
    script_tag = soup.new_tag("script", src="app.js")
    soup.body.append(script_tag)
  # --- ファイル保存 ---
  css_content  = "\n\n".join(css_blocks)
  js_content   = "\n\n".join(js_blocks)
  html_content = soup.prettify()
  (out / "index.html").write_text(html_content, encoding="utf-8")
  (out / "style.css").write_text(css_content,   encoding="utf-8")
  (out / "app.js").write_text(js_content,        encoding="utf-8")
  print(f"✅ 分割完了:")
  print(f"   {out / 'index.html'}  ({len(html_content):,} chars)")
  print(f"   {out / 'style.css'}   ({len(css_content):,} chars)")
  print(f"   {out / 'app.js'}      ({len(js_content):,} chars)")
# ───────────────────────────────
# Step 1: SKILL読み込み
# ───────────────────────────────
## SKILLのパスと出力先パス
SKILL_PATH    = "./skills/frontend-design.md"
skill_text = Path(SKILL_PATH).read_text(encoding="utf-8")
# ───────────────────────────────
# Step 2: 入力トークン量の確認
# ───────────────────────────────
# 一度に読み書きできるコンテキストウィンドウ
CONTEXT_NUM = 16384
## トークン量の確認
SKILL_PATH    = "./skills/frontend-design.md"
skill_text = Path(SKILL_PATH).read_text(encoding="utf-8")
DOC_PATH  = "./docs/desing_doc.md"
doc_text = Path(DOC_PATH).read_text(encoding="utf-8")
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
design_tokens = len(doc_text) / 2  # 日本語: 約2文字/token
system_tokens = skill_tokens + overhead_tokens # system prompt
total = skill_tokens + design_tokens + system_tokens
rest_context = CONTEXT_NUM - total
print(f"SKILL   : {skill_tokens:.0f} tokens")
print(f"設計書  : {design_tokens:.0f} tokens")
print(f"合計(入力): {total:.0f} tokens")
print(f"残り(出力用): {rest_context:.0f} tokens")
# ───────────────────────────────
# Step 3: プロンプトとChain作成
# ───────────────────────────────
google_callback = GoogleMetadataCallback()
llm_api_gemini = ChatGoogleGenerativeAI(
  model="gemini-3.5-flash",
  google_api_key=os.environ['GOOGLE_AI_ST_API'],
  temperature=0,
  callbacks=[google_callback]
)
## プロンプト
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
  | llm_api_gemini
  | StrOutputParser()
)
# ───────────────────────────────
# Step 5: 実行(設計書を渡したパターン)
# ───────────────────────────────
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
  cb_summary = google_callback.summary()
  common.res_output_md(cb_summary,dir_str=OUTPUT_DIR,file_name="callback-summary")
else:
  print(f'''⚠️  エラー: コンテキストウィンドが足りません
        コンテキストウィンドを調整してください。''')
