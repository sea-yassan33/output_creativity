# uv とは

https://docs.astral.sh/uv/

- uvは、Rust言語で開発されたPython向けの高速パッケージマネージャーです。
- 従来のpipと比べて10～100倍の速度でパッケージのインストールや依存関係の解決を行います
- 仮想環境の作成や管理も統合的に行えるオールインワンツールとして設計されています。
- Python開発者の生産性を大幅に向上させます。

# windowsインストール方法

- 管理者権限でPowerShellを起動

```sh
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

# 基本的な使用方法

```sh
# プロジェクト作成
uv init <プロジェクト名>

# 仮想環境作成
uv venv

# インストール
uv add <パッケージ名>

# 仮想感環境を使った動かし方
uv run python main.py

# パッケージ確認
uv pip list

# パッケージuninstall
uv remove <パッケージ名>

# pyproject.tomlでバージョンを変えたとちにupgrade
uv sync --upgrade

# pytestの導入
uv add --dev pytest
```

- .python-version: pythonのバージョン
- uv.lock: 依存関係パッケージも含めたパッケージとその正確なバージョンファイル
- pyproject.toml: プロジェクトに必要なパッケージとそのバージョンの範囲

# チーム間で環境を共有する場合は

下記を共有
- pyproject.toml
- uv.lock
- .python-version

```sh
# 配置後下記を実施
uv sync

# 開発のみのパッケージを除いた実施方法
uv sync --no-dev
```

# テスト方法

```sh
# 仮想環境を汚さずに一時的に実行
uvx pytest

uv cache dir

uv cache clean
```

# テストコード作成

```sh
myproject/
├── src/
│   └── calculator.py
├── tests/
│   └── test_calculator.py
├── pyproject.toml
└── uv.lock
```