# 1_Oracle Linux 9.5
- 2024年11月にリリースされた最新のマイナーアップデート版です
- RHEL 9.5 をベースにしており、最新のハードウェア対応やセキュリティ強化が含まれています。
- HEL 系 OS（CentOS の後継としての AlmaLinux や Rocky Linux など）と同様の感覚で、企業環境でも安心して無料で使い続けることができます。


# 2_WSLにOracle Linux 9.5をインストールする方法

```sh
# PowerShell（管理者権限）で実行
wsl --list --online

## インストール
wsl --install -d OracleLinux_9_5

## 初回起動・ユーザー設定
Enter new UNIX username: （任意のユーザー名）
New password: （パスワード）
Retype new password: （パスワード再入力）

# デフォルトディストリビューションを変更
wsl --set-default OracleLinux_9_5
```

# 3_システム全体のアップデート

```sh
# 管理者権限
# インストール済みパッケージの更新確認
sudo dnf check-update

sudo dnf update
```

# 4_alias設定

```sh
vi ~/.bashrc

## ファイルの末尾に以下を追記する
alias ll='ls -la'
alias ls='ls --color=auto'

## 保存後設定を反映
source ~/.bashrc
```

# 5_Git

## 5-1.Gitインストール
```sh
dnf install -y git openssh-clients

git --version

git config --global init.defaultBranch main
```

## 5-2.Gitの設定

### 【SSHの生成】

```sh
cd ~

mkdir -p ~/.ssh/sample

ssh-keygen -t ed25519 -C "sample@example.com" -f ~/.ssh/sample/sample_key
```

### config 作成

```sh
touch ~/.ssh/config
chmod 600 ~/.ssh/config

vi ~/.ssh/config

## [editer] config
Host github.com
    HostName github.com
    User git
    IdentityFile /home/admin/.ssh/sample/sample_key
```

### SSHエージェントに登録
```sh
## 起動
ssh-agent bash

## 登録
ssh-add ~/.ssh/sample/sample_key

## 登録確認
ssh-add -l

## ログイン時に自動起動させたい場合
vi ~/.bashrc

# SSH Agent 自動起動
if [ -z "$SSH_AUTH_SOCK" ]; then
  eval "$(ssh-agent -s)"
  ssh-add ~/.ssh/sample/sample_key
fi
```

### 公開鍵をコピー

```
cat ~/.ssh/sample/sample_key.pub
```

### gitHubにて設定

●以下にアクセス
- https://github.com/settings/keys

●「New SSH key」をクリック

●下記の内容を登録

- Title: Ubuntu等のわかりやすい名前を登録する。
- Key Type: Authentication Key
- Key : 公開鍵をクリップボードにコピーして、Githubに鍵を登録する


### 接続テスト

```sh
## 接続テスト
ssh -T git@github.com
```

### Gitユーザ登録

```sh
git config --global user.name gitHub_userName

git config --global user.email sample@example.com

# コミットする時に、改行コードを自動的に LF（Unix/Mac形式）に変換
git config --global core.autocrlf input

# 設定内容の確認
git config --global --list
```

### sshでのクローン
```sh 
git clone git@github.com:username/repository.git
```

