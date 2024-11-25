# dg-metadata-manager
特定のストレージから取得したデータを、特定のスキーマ(※)の形式に変換するモジュール

※ NII RDC-APまたはその拡張機能であるDG-APに沿うように内部データを持つスキーマ

## Installation

```bash
pip install git+https://github.com/NII-DG/dg-metadata-manager.git
```

## Usage

```python
from dg_mm import MetadataManager

mm = MetadataManager()
metadata = mm.get_metadata('schema name', 'storage name', token='token for storage access', id='storage id')
```
### schema name
現在使用できるスキーマ名一覧

|スキーマ名|概要|
|---|---|
|RF|リサーチフロー/DG-Webで使用するスキーマ|

### storage name
現在使用できるストレージ名一覧

|ストレージ名|概要|アクセスに必要なパラメータ|
|---|---|---|
|GRDM|GakuNin RDM|token, id(プロジェクトIDを指定)
