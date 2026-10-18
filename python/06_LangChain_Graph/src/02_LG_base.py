# ───────────────────────────────
# ライブラリ
# ───────────────────────────────
import argparse
import logging
import sys
# LangGraph
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
logger = logging.getLogger(__name__)
# ───────────────────────────────
# 1.State を定義
# ───────────────────────────────
class State(TypedDict):
    message: str
# ───────────────────────────────
# 2. ノード（関数）を定義
# ───────────────────────────────
def say_hello(state: State) -> dict:
    return {"message": state["message"] + " こんにちは"}
def say_world(state: State) -> dict:
    return {"message": state["message"] + " 世界"}
# ───────────────────────────────
# 3. グラフを組み立てる
# ───────────────────────────────
def build_graph():
    builder = StateGraph(State)
    builder.add_node("hello", say_hello)
    builder.add_node("world", say_world)
    builder.add_edge(START, "hello")   # 開始 → hello
    builder.add_edge("hello", "world") # hello → world
    builder.add_edge("world", END)     # world → 終了
    graph = builder.compile()
    return graph
# ───────────────────────────────
# 4.実行
# ───────────────────────────────
def main():
    ## argparse
    arg_parser = argparse.ArgumentParser(description="はじめてのLangGraph")
    arg_parser.add_argument("request", help="メッセージを入力します")
    args = arg_parser.parse_args()
    request = args.request
    try:
        # LangGraphコンパイル
        lg_compile = build_graph()
        result = lg_compile.invoke({"message": request})
        print(result["message"])
    except Exception:
        logger.exception("失敗しました")
        sys.exit(1)
if __name__ == "__main__":
    main()
