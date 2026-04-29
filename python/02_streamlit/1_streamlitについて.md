# 【Streamlitについて】

## 01.Streamlitとは

- Streamlit（ストリームリット）は、Pythonだけで機械学習やデータ分析用の対話型Webアプリを爆速で開発できるオープンソースのフレームワークです。
- HTML/CSS/JSの知識は不要で、Pythonスクリプトを数行書くだけでグラフやウィジェットを実装可能。

## 02.主な特徴とメリット
- **Pythonのみで完結:** データ処理のスクリプトをWebアプリに変換できます。
- **高速開発:** 視覚的なUI（ボタン、スライダー、グラフ）が短いコードで実装可能。
- **即時反映:** ソースコードの修正が即座にブラウザに反映される（オートリロード）。
- **データ連携:** Plotly、Matplotlibなどと親和性が高く、インタラクティブなダッシュボード作成に最適。

## 03. インストールと起動

```sh
# インストール
pip install streamlit

# アプリの起動
streamlit run app.py

# バージョン確認
streamlit --version
```

**最小構成の `app.py`:**

```python
import streamlit as st

st.title("Hello, Streamlit!")
```

## 04.config.tomlについて

**「config.toml」**とはStreamlit アプリの動作や見た目を細かく設定するための設定ファイルです。

### 【ファイルの場所】

```txt
your_project/
└── .streamlit/
    └── config.toml   ← ここに作成
```

### 作成手順

```sh
mkdir .streamlit
touch .streamlit/config.toml
```

### 主な設定

```sh
[server]
port = 8501                  # ポート番号（デフォルト: 8501）
headless = true              # ブラウザを自動で開かない（サーバー運用時に便利）
runOnSave = true             # ファイル保存時に自動リロード
maxUploadSize = 200          # アップロード上限 MB（デフォルト: 200）

[browser]
gatherUsageStats = false     # 使用状況の送信をオフ

[theme]
base = "light"               # "light" or "dark"
primaryColor = "#FF4B4B"     # アクセントカラー（ボタン・スライダーなど）
backgroundColor = "#FFFFFF"  # 背景色
secondaryBackgroundColor = "#F0F2F6"  # サイドバー・カードの背景色
textColor = "#262730"        # テキストカラー
font = "sans serif"          # "sans serif" / "serif" / "monospace"

[logger]
level = "info"               # "debug" / "info" / "warning" / "error"

[client]
toolbarMode = "viewer"       # "auto" / "developer" / "minimal"
```

- clientの設定値

| 値 | 動作 |
|---|---|
| `"auto"` | デフォルト。開発時は表示、`headless=true` 時は最小化 |
| `"developer"` | 常にフル表示（再実行・設定・レコードなど全メニュー表示） |
| `"viewer"` | 最小限の表示（一般ユーザー向けに余分なメニューを非表示） |
| `"minimal"` | ツールバーを完全に非表示 |

## 05. テキスト表示

| 関数 | 用途 | 例 |
|------|------|-----|
| `st.title()` | ページタイトル（H1相当） | `st.title("マイアプリ")` |
| `st.header()` | セクション見出し（H2相当） | `st.header("セクション1")` |
| `st.subheader()` | サブ見出し（H3相当） | `st.subheader("小見出し")` |
| `st.text()` | 等幅プレーンテキスト | `st.text("固定幅テキスト")` |
| `st.markdown()` | Markdown形式テキスト | `st.markdown("**太字**")` |
| `st.caption()` | 小さなキャプション | `st.caption("注釈テキスト")` |
| `st.code()` | コードブロック | `st.code("x = 1", language="python")` |
| `st.latex()` | LaTeX数式 | `st.latex(r"E = mc^2")` |
| `st.write()` | 万能表示（型を自動判定） | `st.write("何でも表示")` |
| `st.divider()` | 区切り線 | `st.divider()` |

```python
st.title("タイトル")
st.header("ヘッダー")
st.subheader("サブヘッダー")
st.markdown("**Markdown** で *スタイル* 適用")
st.code("""
def hello():
    return "Hello, World!"
""", language="python")
st.latex(r"\sum_{i=1}^{n} x_i")
```

---

## 06. データ表示

| 関数 | 用途 |
|------|------|
| `st.dataframe()` | インタラクティブなDataFrame表示 |
| `st.table()` | 静的なテーブル表示 |
| `st.metric()` | KPI・指標の表示 |
| `st.json()` | JSON形式で表示 |
| `st.write()` | DataFrame・辞書など自動判定で表示 |

```python
import pandas as pd
import streamlit as st

df = pd.DataFrame({
    "名前": ["Alice", "Bob", "Carol"],
    "年齢": [25, 30, 28],
    "スコア": [88.5, 92.0, 79.3],
})

# インタラクティブなテーブル（ソート・スクロール可）
st.dataframe(df, use_container_width=True)

# 静的テーブル
st.table(df)

# KPI指標（delta で増減表示）
st.metric(label="売上", value="¥1,200,000", delta="+¥50,000")

# JSON表示
st.json({"key": "value", "numbers": [1, 2, 3]})
```

---

## 07. グラフ・チャート

### Streamlit 組み込みチャート

| 関数 | 用途 |
|------|------|
| `st.line_chart()` | 折れ線グラフ |
| `st.bar_chart()` | 棒グラフ |
| `st.area_chart()` | 面グラフ |
| `st.scatter_chart()` | 散布図 |
| `st.map()` | 地図（緯度・経度） |

```python
import numpy as np
import pandas as pd
import streamlit as st

data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["A", "B", "C"]
)

st.line_chart(data)
st.bar_chart(data)
st.area_chart(data)
```

### 外部ライブラリとの連携

```python
import matplotlib.pyplot as plt
import plotly.express as px

# Matplotlib
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
st.pyplot(fig)

# Plotly
fig = px.scatter(df, x="年齢", y="スコア", color="名前")
st.plotly_chart(fig, use_container_width=True)
```

---

## 08. 入力ウィジェット

| 関数 | 用途 | 戻り値 |
|------|------|--------|
| `st.button()` | ボタン | `bool` |
| `st.checkbox()` | チェックボックス | `bool` |
| `st.radio()` | ラジオボタン | 選択値 |
| `st.selectbox()` | ドロップダウン選択 | 選択値 |
| `st.multiselect()` | 複数選択 | `list` |
| `st.slider()` | スライダー | 数値 or タプル |
| `st.text_input()` | テキスト入力（1行） | `str` |
| `st.text_area()` | テキスト入力（複数行） | `str` |
| `st.number_input()` | 数値入力 | `int` / `float` |
| `st.date_input()` | 日付選択 | `date` |
| `st.time_input()` | 時刻選択 | `time` |
| `st.file_uploader()` | ファイルアップロード | `UploadedFile` |
| `st.color_picker()` | カラーピッカー | `str`（HEX） |
| `st.toggle()` | トグルスイッチ | `bool` |

```python
# ボタン
if st.button("クリック"):
    st.write("ボタンが押されました！")

# スライダー
age = st.slider("年齢を選択", min_value=0, max_value=100, value=25)
st.write(f"選択された年齢: {age}")

# セレクトボックス
option = st.selectbox("言語を選択", ["Python", "JavaScript", "Go"])
if option == "Python":
  st.code("print('Hello, World!')", language="python")
elif option == "JavaScript":
  st.code("console.log('Hello, World!')", language="javascript")
elif option == "Go":
  st.code('fmt.Println("Hello, World!")', language="go")

# セレクト（インデックス）
options = ["Python", "JavaScript", "Go"]
option = st.selectbox("言語を選択", options)
index = options.index(option)  # 選択されたインデックス番号
st.write(f"インデックス: {index}, 値: {option}")

# テキスト入力
name = st.text_input("名前を入力", placeholder="例: 山田 太郎")

# ファイルアップロード
uploaded = st.file_uploader("CSVをアップロード", type=["csv"])
if uploaded:
  df = pd.read_csv(uploaded)
  st.dataframe(df)

# 範囲スライダー
price_range = st.slider("価格帯", 0, 10000, (2000, 8000))
```

---

## 09. レイアウト

### カラム（列）

```python
col1, col2, col3 = st.columns(3)
with col1:
  st.header("列 1")
  st.write("左側のコンテンツ")
with col2:
  st.header("列 2")
  st.write("中央のコンテンツ")
with col3:
  st.header("列 3")
  st.write("右側のコンテンツ")

# 幅の比率を指定
col_wide, col_narrow = st.columns([3, 1])
```

### エクスパンダー（折りたたみ）

```python
with st.expander("詳細を表示"):
  st.write("ここに詳細なコンテンツが入ります")
  st.image("https://example.com/image.png")
```

### タブ

```python
tab1, tab2, tab3 = st.tabs(["データ", "グラフ", "設定"])

with tab1:
  st.write("データタブの内容")

with tab2:
  st.line_chart(data)

with tab3:
  st.write("設定タブの内容")
```

### サイドバー

```python
# サイドバーにウィジェットを配置
with st.sidebar:
  st.header("フィルター設定")
  category = st.selectbox("カテゴリ", ["全て", "A", "B", "C"])
  min_val = st.slider("最小値", 0, 100, 10)

# 省略記法
st.sidebar.write("サイドバーのテキスト")
```

---

## 10. メディア

```python
# 画像表示
st.image("./image.png", caption="サンプル画像", use_container_width=True)
st.image("https://example.com/photo.jpg", width=300)

# 動画表示
st.video("./video.mp4")

# 音声再生
st.audio("./audio.mp3")
```

---

## 11. 状態管理（Session State）

- Streamlitはユーザー操作のたびにスクリプト全体を再実行します。`session_state` を使うとデータを保持できます。

```python
import streamlit as st

# 初期化
if "count" not in st.session_state:
    st.session_state.count = 0

# 更新
if st.button("カウントアップ"):
    st.session_state.count += 1

if st.button("リセット"):
    st.session_state.count = 0

st.write(f"カウント: {st.session_state.count}")

# コールバック関数を使った更新
def increment():
    st.session_state.count += 1

st.button("コールバックで増やす", on_click=increment)
```

---

## 12. キャッシュ

- 重い計算やデータ読み込みをキャッシュしてパフォーマンスを改善します。

| デコレータ | 用途 |
|-----------|------|
| `@st.cache_data` | データ（DataFrame, 数値など）のキャッシュ |
| `@st.cache_resource` | リソース（DB接続, MLモデルなど）のキャッシュ |

```python
import streamlit as st
import pandas as pd
import time

# データキャッシュ（DataFrameや計算結果に使用）
@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
  time.sleep(2)  # 重い処理を想定
  return pd.read_csv(filepath)

# リソースキャッシュ（接続やモデルに使用）
@st.cache_resource
def load_model():
  # 機械学習モデルの読み込みなど
  return SomeLargeModel()

df = load_data("data.csv")  # 初回のみ実行、以降はキャッシュから返す
st.dataframe(df)

# キャッシュの有効期限設定（秒）
@st.cache_data(ttl=3600)
def fetch_api_data():
  ...

# キャッシュの手動クリア
load_data.clear()
```

### 「@st.cache_data」と「@st.cache_resource」の違い

| | `@st.cache_data` | `@st.cache_resource` |
|---|---|---|
| **対象** | データ（DataFrame、数値、文字列） | リソース（DB接続、モデル、クライアント） |
| **コピー方法** | 呼び出しごとに**コピーを返す** | **同一オブジェクト**を返す |
| **スレッド安全** | ✅ 安全 | ⚠️ 自分で管理が必要 |
| **用途** | クエリ結果・計算結果 | コネクションプール・MLモデル |


MySQL接続オブジェクト  → @st.cache_resource  （一度だけ接続）
クエリ結果のDataFrame → @st.cache_data      （安全にコピーして返す）

### MySQLの場合の正しい使い方

```python
import streamlit as st
import mysql.connector
import pandas as pd

# 接続クライアントは cache_resource
@st.cache_resource
def get_connection():
  return mysql.connector.connect(
    host="localhost",
    user="user",
    password="password",
    database="mydb"
  )

# クエリ結果は cache_data
@st.cache_data(ttl=600)  # 10分キャッシュ
def fetch_data(query: str) -> pd.DataFrame:
  conn = get_connection()
  return pd.read_sql(query, conn)

# 使用
df = fetch_data("SELECT * FROM users")
st.dataframe(df)
```

---

## 10. 通知・フィードバック

| 関数 | 用途 | 色 |
|------|------|-----|
| `st.success()` | 成功メッセージ | 緑 |
| `st.info()` | 情報メッセージ | 青 |
| `st.warning()` | 警告メッセージ | 黄 |
| `st.error()` | エラーメッセージ | 赤 |
| `st.exception()` | 例外の詳細表示 | 赤 |
| `st.toast()` | トースト通知（一時表示） | — |
| `st.spinner()` | ローディングスピナー | — |
| `st.progress()` | プログレスバー | — |
| `st.balloons()` | 風船アニメーション 🎈 | — |
| `st.snow()` | 雪アニメーション ❄️ | — |

```python
st.success("処理が完了しました！")
st.info("情報: データを読み込んでいます")
st.warning("警告: データが古い可能性があります")
st.error("エラー: ファイルが見つかりません")
st.toast("保存しました！", icon="✅")

# スピナー
with st.spinner("処理中..."):
    time.sleep(3)
st.success("完了！")

# プログレスバー
bar = st.progress(0)
for i in range(100):
    bar.progress(i + 1)
    time.sleep(0.01)
```

---

## 11. ページ設定

```python
import streamlit as st

st.set_page_config(
    page_title="マイアプリ",           # ブラウザタブのタイトル
    page_icon="🚀",                    # ファビコン（絵文字 or 画像パス）
    layout="wide",                     # "centered"（デフォルト） or "wide"
    initial_sidebar_state="expanded",  # "expanded" or "collapsed" or "auto"
    menu_items={
        "Get Help": "https://example.com/help",
        "Report a bug": "https://example.com/bug",
        "About": "# マイStreamlitアプリ v1.0",
    }
)
```

## 12.実装例

### データフィルタリングアプリ

```python
import streamlit as st
import pandas as pd

st.title("データフィルタリング")

uploaded = st.file_uploader("CSVをアップロード", type="csv")
if uploaded:
  df = pd.read_csv(uploaded)
  with st.sidebar:
    cols = st.multiselect("表示列", df.columns.tolist(), default=df.columns.tolist())
  st.dataframe(df[cols], use_container_width=True)
  st.download_button("CSVダウンロード", df[cols].to_csv(index=False), "filtered.csv")
```

### リアルタイム更新

```python
import streamlit as st
import time

placeholder = st.empty()
for i in range(10):
  with placeholder.container():
    st.metric("カウンター", i)
    st.progress(i / 9)
  time.sleep(1)
```