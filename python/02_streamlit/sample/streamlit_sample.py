# ---------------------------------------------------------------------------
# ライブラリー：　pip install streamlit pandas
# 起動方法： streamlit run streamlit_sample.py
# ---------------------------------------------------------------------------
import streamlit as st
import pandas as pd

# データフレームを出力
df = pd.DataFrame({
    "名前": ["Alice", "Bob", "Carol"],
    "年齢": [25, 30, 28],
    "スコア": [88.5, 92.0, 79.3],
})
st.dataframe(df, use_container_width=True, hide_index=True)