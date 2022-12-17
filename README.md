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

- Python : 3.10.8


## リポジトリ構成

```
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
