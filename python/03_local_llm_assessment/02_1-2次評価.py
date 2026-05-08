import warnings
# 警告を非表示にする
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True
import os
from dotenv import load_dotenv
load_dotenv()
import common_func
from common_func import GoogleMetadataCallback
## LangChain系ライブラリ
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.evaluation import load_evaluator, EmbeddingDistance
## model
embeddings = HuggingFaceEmbeddings(model_name="sonoisa/sentence-bert-base-ja-en-mean-tokens-v2")
llm = ChatOllama(model="gemma3:4b",base_url=os.environ['OLLAM_URL'],temperature=0.0)
llm_api_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.environ['GOOGLE_AI_ST_API'], temperature=0)
## 定数
meta_map = {}
# 関数
def evaluation_analysis01(assesment,target_text: str, expected_text: str):
  """
  評価出力関数
  target_text: 生成したコンテンツ
  expected_text: 期待されるコンテンツ
  """
  # --- １次評価: テキスト長の比較 ---
  gen_len = len(target_text)
  ref_len = len(expected_text)
  ratio   = gen_len / ref_len if ref_len > 0 else 0
  print(f"\n【長さの比較】")
  print(f"  生成: {gen_len}文字 / 参照: {ref_len}文字 (比率: {ratio:.2f})")
  if ratio < 0.5:
    print("  ⚠️ 原因候補: 生成が短すぎる → 情報が欠落している可能性")
  elif ratio > 2.0:
    print("  ⚠️ 原因候補: 生成が長すぎる → 余分な情報が含まれている可能性")
  else:
    print("  ✅ 長さは適切")
  print("\n" + "="*50)
  # --- 2次評価: セマンティック評価 ---
  print("📋 セマンティック評価結果")
  print("="*50)
  distance = assesment["score"]
  similarity = 1 - distance
  print(f"コサイン距離:   {distance:.4f}  （0に近いほど良い）")
  print(f"類似度スコア:   {similarity:.4f}  （1に近いほど良い）")
  print(f"評価結果:       {'✅ 良好' if similarity >= 0.8 else '⚠️ 要改善' if similarity >= 0.6 else '❌ 不十分'}")
  print("\n" + "="*50)
  print("📋 評価の分析Part1")
  print("="*50)
  return similarity
# ============================================================
# ① 準備
# ============================================================
## 生成された概要
with open("./data/test03-summary.md", "r", encoding="utf-8") as f:
  final_summary = f.read()
# ============================================================
# Step 2: セマンティック評価
# ============================================================
# 評価器のセットアップ
evaluator = load_evaluator(
    "embedding_distance",           # 予測 vs 参照の比較
    embeddings=embeddings,   # ローカルEmbedding
    distance_metric=EmbeddingDistance.COSINE  # 自然言語に最適
)
# 論文の概要
with open("./data/paper01_oberveiw.md", "r", encoding="utf-8") as f:
  expected_text = f.read()
print("=== セマンティック評価開始 ===")
res_assesment = evaluator.evaluate_strings(
  prediction=final_summary,
  reference=expected_text
)
# ============================================================
# Step 3: セマンティック評価の分析
# ============================================================
similarity = evaluation_analysis01(res_assesment,final_summary,expected_text)
# ============================================================
# Step 4: LLMによる定性評価
# ============================================================
## 評価用テンプレート
analysis_prompt = ChatPromptTemplate.from_template("""
あなたは文章評価の専門家です。
以下の「生成された概要」と「参照概要」を比較し、
類似度が低い原因を日本語で簡潔に指摘してください。

生成された概要:
{generated}

参照概要:
{reference}

類似度スコア: {similarity:.2f}（1.0が最高）

指摘（箇条書き）:
""")
## chain
chain = analysis_prompt | llm_api_gemini | StrOutputParser()
google_callback = GoogleMetadataCallback()
analysis = chain.invoke({
  "generated":  final_summary,
  "reference":  expected_text,
  "similarity": similarity
},config={"callbacks": [google_callback]})
meta_map["llm_call2-01"] = google_callback
# ============================================================
# Step 5: summaryの出力とトークン量の確認
# ============================================================
## summary内容出力
myfunc.res_output_md(response=analysis,file_name=f"test03-summary-analysis")
## LLMトークン量確認
myfunc.token_check(meta_map)