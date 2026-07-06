# python基礎コード備忘録

# 【1.基礎】
## 1-1.ディレクトリ作成

```py
from pathlib import Path
dir_path = Path("./out/")
# parents=True: 親ディレクトリもなければ作成する
# exist_ok=True: 既に存在していてもエラーにしない
dir_path.mkdir(parents=True, exist_ok=True)
```

## 1-2.警告文の非表示
```py
import warnings
warnings.filterwarnings('ignore')
```

## 1-3.pycahe作成しない
```py
import sys
sys.dont_write_bytecode = True
```

## 1-4.envファイル読み込み
```py
import os
from dotenv import load_dotenv
## .envファイル読込み
load_dotenv()
youtude_key = os.environ['KEY']
```

## 1-5.pythonを動かすshellスクリプト
```py
import sys
# コマンドライン引数を表示（sys.argv[0] はスクリプト自身の名前）
print("引数の数:", len(sys.argv))
print("引数一覧:", sys.argv)
# それぞれの引数を取り出す
arg1 = sys.argv[1]
print(f"1番目の引数: {arg1}")
```

```sh
#!/bin/bash
#
## 引数読み込み
if [ -z "$1" ]; then
  echo "Error: 引数を指定してください"
  echo "引数例: $0 \"1,2,3\""
  exit 1
fi
echo "引数: $1"
echo
echo "pythonを実行します"
# Pythonスクリプトを実行
python sample.py "$1"
```

# 【2.Pandas】
## 2-1データ結合
```py
import pandas as pd
# 複数のデータフレームを縦結合する方法
# 例：3つのデータフレーム
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
df3 = pd.DataFrame({'A': [9, 10], 'B': [11, 12]})

# 縦結合（インデックスは再利用される）
df_concat = pd.concat([df1, df2, df3])
df_concat.reset_index(drop=True, inplace=True)
print("縦結合したデータフレーム:")
print(df_concat)
```

## 2-2.複数のCSVファイルからDataFrameに変換
```py
import pandas as pd
import glob
# 対象ディレクトリのパス（例：'./data'）
directory = './data'
# CSVファイルのパス一覧を取得
csv_files = glob.glob(os.path.join(directory, '*.csv'))
# 各CSVファイルをDataFrameとして読み込む
dataframes = [pd.read_csv(file) for file in csv_files]
```

## 2-3.並び替え
```py
# データフレームで列をして並べ替えする方法
# 昇順（小さい順）: デフォルト（ascending=True）
# 降順（大きい順）: ascending=False
df_concat.sort_values(by=['A', 'B'], ascending=[False, False])
```

## 2-4.相違のある行を抽出
```py
#相違のある行を抽出（行単位で比較）
diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
print(diff)

#差分を具体的に知る
diff = df1.compare(df2)
```

## 2-5.結合
```py
df1 = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie']
})
df2 = pd.DataFrame({
    'id': [1, 2, 4],
    'score': [85, 90, 70]
})
# idをキーに横結合（内部結合：共通のidのみ残る）
merged = pd.merge(df1, df2, on='id')

# 内部結合（共通するキーだけ）← デフォルト
pd.merge(df1, df2, on='id', how='inner')
# 左外部結合（df1のすべて + 共通部分）
pd.merge(df1, df2, on='id', how='left')
# 右外部結合（df2のすべて + 共通部分）
pd.merge(df1, df2, on='id', how='right')
# 完全外部結合（全てのキーを含める）
pd.merge(df1, df2, on='id', how='outer')
```