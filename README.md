# dg-metadata-manager

dg-metadata-managerリポジトリ

## 概要

RO-Crate作成と管理およびRO-Crateの検証結果の管理を行うWebアプリケーション。

## ブランチ説明

- master : master（本番環境）ブランチ。develop/ or hotifix/からプルリクエストされる。
- develop/{リリース番号} : 開発（テスト環境）ブランチ。開発中の使用するブランチ。develop/ブランチからプルリクエストされる。
- feature/{開発名} : 機能開発ブランチ。develop/ブランチからブランチが作成される。
- hotifix/{リリース番号} : 修正ブランチ。masterブランチからブランチが作成される。
- release/{リリース番号}/{001から始まる３桁の一連番号} : リリースブランチ。masterブランチからブランチが作成される。


## 環境情報

### 開発言語

- Python : 3.10

### 仮想環境

- venv : Python3.3より標準パッケージとなった仮想環境操作モジュール

1. 仮想環境の作成

   - インストールされているPythonバージョンを確認する。（Python3.10系がインストールされていればOK）

   ```bash
   # インストール済みのpythonバージョン一覧
    py --list-paths

    # output
    -V:3.11 *        C:\Users\*****\MyApp\Python\3.11\python.exe
    -V:3.10          C:\Users\*****\MyApp\Python\3.10\python.exe
   ```

   - Python 3.10 で仮想環境を作成する。仮想環境名=env-dg-mm

   ```bash
    # pythonバージョンと仮想環境名を指定して仮想環境を作成する。
    # py -{python version} -m venv env-{環境名}
    py -3.10 -m venv env-dg-mm
   ```

   ※環境名の頭文字env-は必ず付けてください。（バージョン管理対象外にするため）

2. 仮想環境の有効化

   ```bash
    # env-{環境名}/Scripts/Activate.ps1
    env-dg-mm/Scripts/Activate.ps1
   ```
   ※このシステムではスクリプトの実行が無効になっているため、....を読み込めない。とメッセージが表示された場合は、 PowerShellでSet-ExecutionPolicy RemoteSigned -Scope CurrentUser -Forceを実行してからやり直す。

   環境の有効化が成功すると、(env-dg-mm)がターミナル行の先頭に表示される。

3. 仮想環境の無効化

   ```bash
   deactivate
   ```

4. パッケージインストール
   ※仮想環境が有効状態で行う
   ※新規にパッケージをインストールする場合に用いる

   ```bash
   pip install {パッケージ名}
   ```

5. パッケージリストの作成

   ※仮想環境が有効状態で行う
   ※githubにコミットする前に実行してください。

    ```bash
    pip freeze > requirements.txt
    ```

6. パッケージリストを用いてパッケージをインストールする

    ※仮想環境が有効状態で行う
    ※`git pull`や`git clone`をした場合は、実行してください。

    ```bash
    pip install -r requirements.txt
    ```

## リポジトリ構成

```bash
/
├ api/
│ ├ controllers/         コントローラクラスファイルを格納するディレクトリ
│ │ └ xxxxxxxxxxx.py     コントローラクラスファイル
│ ├ logics/               ロジッククラスファイルを格納するディレクトリ
│ │ └ xxxxxxxxxxx.py     ロジッククラスファイル
│ ├ models/              モデルクラスファイルを格納するディレクトリ
│ │ └ xxxxxxxxxxx.py     モデルクラスファイル
│ ├ utils/               共通モジュールディレクトリ
│ └ __init__.py
├ instance/
│ └ config/              設定フォルダ
│    ├ local.py
│    ├ development.py
│    ├ staging.py
│    └ production.py
├ log/
├ tests/
├ application.py          複数のファイルが利用するものを定義（Flaskインスタンス、DB、環境変数など）
├ manager.py             アプリ実行用スクリプト（アプリの入り口）
├ requirements.py        ライブラリ一覧
├ settings.py
├ setup.py
└ www.py                 ルーティングをFlaskアプリケーションに登録するファイル
```

## データベースの設定（ローカル）

- DBとしてMySQLを使用する。Ubuntu上でMySQLコンテナを作成する。

```bash
docker pull mysql:8.0.31

docker run -d --name test_mysql -e MYSQL_ROOT_PASSWORD=mysql -p 3306:3306 mysql:8.0.31
　
docker exec -it test_mysql bash -p

mysql -u root -p -h 127.0.0.1
```

- DBユーザとデータベースを作成する。

```bash
-- gin fork 用のデータベースを作成（データベース名はgin forkの設定ファイル記述する。）
CREATE DATABASE dg_mm_db;
SHOW databases;

-- データベースの管理ユーザとパスワードを設定する。 （gin forkの設定ファイル記述する。）
CREATE USER 'test_user'@'%' IDENTIFIED BY 'test_pw';
SELECT user, host FROM mysql.user;

-- ユーザ権限を付与する
GRANT ALL ON dg_mm_db.* TO 'test_user'@'%';
FLUSH PRIVILEGES;
```
