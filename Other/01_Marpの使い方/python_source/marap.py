# ───────────────────────────────
# ライブラリ
# ───────────────────────────────
import argparse
import logging
import sys
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import TypedDict
from dataclasses import dataclass
# LangGraph
from langgraph.graph import StateGraph, END
# LangChain
from langchain_core.messages import HumanMessage, SystemMessage
# provider
from langchain_ollama import ChatOllama
# ───────────────────────────────
# 定数
# ───────────────────────────────
load_dotenv()
logger = logging.getLogger(__name__)
# ルート
DOC_DIR = Path(__file__).resolve().parent
OUTPUT_DIR="out"
# 出力: 結合後の最終スライド
OUTPUT_MD = DOC_DIR / OUTPUT_DIR / "slides.md"
# 中間生成物（セクション毎のスライド断片）の保存先
WORK_DIR = DOC_DIR / OUTPUT_DIR / "work"
# スライド区切り
SLIDE_SEPARATOR = "\n\n---\n\n"
# slides.md 冒頭に付与する Marp 設定
FRONT_MATTER = """---
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
"""
# ───────────────────────────────
# 1.Markdownを分割するクラス・関数
# ───────────────────────────────
# """元 Markdown をセクション(##)単位へ分割するモジュール。
# - 先頭の `#`(H1) は資料全体の表題として扱う。
# - `##`(H2) 毎に1セクションとして切り出す。
# - `---`(水平線) は元資料内の区切りなので分割時に除去する。
# """
@dataclass
class Section:
    """1つの ## セクションを表す。"""
    index: int          # 出現順(1始まり)
    heading: str        # 見出しテキスト(## を除く)
    body: str           # 見出しを含むセクション本文
@dataclass
class Document:
    """分割結果全体。"""
    title: str              # 先頭 # の表題
    sections: list[Section]
def _strip_hr_lines(text: str) -> str:
    """行単独の水平線(---)を取り除く。"""
    lines = [ln for ln in text.splitlines() if ln.strip() != "---"]
    return "\n".join(lines).strip()
def split_markdown(md_path: Path) -> Document:
    """Markdown ファイルを表題とセクション群へ分割する。"""
    raw = Path(md_path).read_text(encoding="utf-8")
    # 表題(先頭の # 見出し)を抽出
    title_match = re.search(r"^\#\s+(.+)$", raw, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "無題"
    # ## で始まる位置を全て取得して区切る
    heading_positions = [m.start() for m in re.finditer(r"^\#\#\s+", raw, flags=re.MULTILINE)]
    sections: list[Section] = []
    for i, start in enumerate(heading_positions):
        end = heading_positions[i + 1] if i + 1 < len(heading_positions) else len(raw)
        chunk = raw[start:end]
        body = _strip_hr_lines(chunk)
        heading_line = body.splitlines()[0] if body else ""
        heading = re.sub(r"^\#\#\s+", "", heading_line).strip()
        sections.append(Section(index=i + 1, heading=heading, body=body))
    return Document(title=title, sections=sections)
# ───────────────────────────────
# 2. プロンプト
# ───────────────────────────────
## ----システムプロンプト----
SYSTEM_PROMPT = """あなたはMarpスライド作成の専門家です。
与えられたMarkdownの1セクションを、Marp形式のスライド本文へ変換します。

厳守事項:
- 出力はスライド本文のMarkdownのみ。フロントマターやコードフェンス(```)で全体を囲まない。
- 見出しは `##` を維持する。元の見出しテキストは変更しない。
- 表・箇条書き・コードブロックは元の情報を保持する。
- 1枚(size: 16:9)に収まらない情報量の場合のみ、`---` で区切って複数スライドに分割してよい。
  その際、続きのスライドにも同じ `## 見出し` を付ける。
- 説明を追加したり要約しすぎたりせず、元の内容に忠実に整形する。
- 前置きや後書き(「以下が変換結果です」等)は一切書かない。
"""
## ----ユーザープロンプト----
USER_TEMPLATE = """次のセクションをMarpスライド本文へ変換してください。

--- 対象セクション ---
{body}
"""
# ───────────────────────────────
# 3.State を定義
# ───────────────────────────────
class GraphState(TypedDict):
    """ワークフロー全体で共有する状態。"""
    source_path: str          # 入力Markdownパス
    document: Document        # 分割結果
    cursor: int               # 次に処理するセクションのindex(0始まり)
    fragments: list[str]      # 生成済みスライド断片(セクション順)
    output_path: str          # 出力パス
    result_path: str          # 実際に書き出したパス
# ───────────────────────────────
# 4．モデル設定
# ───────────────────────────────
def _build_llm() -> ChatOllama:
    """設定に従い Ollama チャットモデルを生成する。"""
    return ChatOllama(
        model="gemma4:e4b",
        base_url=os.environ["OLLAM_URL"],
        temperature=0.2,
        num_ctx=16384
    )
# ───────────────────────────────
# 5. ノード（関数）を定義
# ───────────────────────────────
def node_split(state: GraphState) -> GraphState:
    """入力Markdownをセクションへ分割する。"""
    doc = split_markdown(Path(state["source_path"]))
    print(f"[split] 表題='{doc.title}' セクション数={len(doc.sections)}")
    state["document"] = doc
    state["cursor"] = 0
    state["fragments"] = []
    return state
def node_generate(state: GraphState) -> GraphState:
    """cursor が指すセクションを1つ生成する。"""
    doc = state["document"]
    section: Section = doc.sections[state["cursor"]]
    print(f"[generate] ({section.index}/{len(doc.sections)}) {section.heading}")
    llm = _build_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=USER_TEMPLATE.format(body=section.body)),
    ]
    response = llm.invoke(messages)
    fragment = _clean_fragment(response.content)
    # 中間生成物を保存(デバッグ・再利用用)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    work_file = WORK_DIR / f"section_{section.index:02d}.md"
    work_file.write_text(fragment, encoding="utf-8")
    state["fragments"].append(fragment)
    state["cursor"] += 1
    return state
def node_merge(state: GraphState) -> GraphState:
    """表題スライド+目次+各断片を結合して slides.md を書き出す。"""
    doc = state["document"]
    # 1. 表題スライド(title クラス)
    title_slide = f"<!-- _class: title -->\n\n# {doc.title}"
    # 2. 目次スライド(toc クラス)
    sections = list(doc.sections)
    chunks = [sections[i:i+6] for i in range(0, len(sections), 6)]
    toc_slides = []
    for chunk in chunks:
        toc_items = "\n".join(f"{s.heading}" for s in chunk)
        toc_slides.append(f"<!-- _class: toc -->\n\n## 目次\n\n{toc_items}")
    toc_slide = SLIDE_SEPARATOR.join(toc_slides)
    # 3. 本文スライド群
    slides = [title_slide, toc_slide, *state["fragments"]]
    body = SLIDE_SEPARATOR.join(slides)
    final = FRONT_MATTER + "\n" + body + "\n"
    out_path = Path(state["output_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(final, encoding="utf-8")
    print(f"[merge] 出力: {out_path}")
    state["result_path"] = str(out_path)
    return state
def _clean_fragment(text: str) -> str:
    """モデル出力から不要なコードフェンス囲みや前後空白を除去する。"""
    t = text.strip()
    # 全体を ```markdown ... ``` で囲っている場合に剥がす
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t
# ───────────────────────────────
# 5. 分岐条件を定義
# ───────────────────────────────
def _should_continue(state: GraphState) -> str:
    """未処理セクションが残っていれば generate を継続する。"""
    if state["cursor"] < len(state["document"].sections):
        return "generate"
    return "merge"
# ───────────────────────────────
# 6. グラフを組み立てる
# ───────────────────────────────
def build_graph():
    """LangGraph のワークフローをコンパイルして返す。"""
    graph = StateGraph(GraphState)
    graph.add_node("split", node_split)
    graph.add_node("generate", node_generate)
    graph.add_node("merge", node_merge)
    graph.set_entry_point("split")
    graph.add_conditional_edges("split", _should_continue, {"generate": "generate", "merge": "merge"})
    graph.add_conditional_edges("generate", _should_continue, {"generate": "generate", "merge": "merge"})
    graph.add_edge("merge", END)
    return graph.compile()
def main():
    ## argparse
    arg_parser = argparse.ArgumentParser(description="スライド生成ツール")
    arg_parser.add_argument("filename", help="ファイル名を入力します")
    arg_parser.add_argument("--output", default="out", help="結果の出力先")
    args = arg_parser.parse_args()
    filename = args.filename
    SOURCE_MD = DOC_DIR / "doc" / filename
    try:
        if SOURCE_MD.exists():
            lg_compile = build_graph()
            initial: GraphState = {
                    "source_path": str(SOURCE_MD),
                    "document": None,
                    "cursor": 0,
                    "fragments": [],
                    "output_path": str(OUTPUT_MD),
                    "result_path": "",
                }
            lg_compile.invoke(initial, {"recursion_limit": 100})
        else:
            print(f"【エラー】{SOURCE_MD}、ファイルパスを確認してください")
    except Exception:
        logger.exception("失敗しました")
        sys.exit(1)
if __name__ == "__main__":
    main()