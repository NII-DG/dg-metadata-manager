import json
import os
import pytest


@pytest.fixture
def create_dummy_definition():
    """テスト用のダミーのマッピング定義ファイルを作成します。"""
    # 前処理
    schema = 'dummy'
    storage = 'dummy'
    path = f'dg_mm/data/mapping/{storage}_{schema}_mapping.json'
    # ファイル作成
    with open(path, mode='w') as f:
        f.write('dummy text')

    yield schema, storage

    # 後処理
    # ファイル削除
    os.remove(path)

@pytest.fixture
def create_test_definition():
    """テスト用のマッピング定義ファイルを作成します。"""
    # 前処理
    schema = 'test_schema'
    storage = 'test_storage'
    path = f'dg_mm/data/mapping/{storage}_{schema}_mapping.json'
    # ファイル作成
    with open(path, mode='w') as f:
        json.dump({"test_property": {"test_definition": "value"}}, f)

    yield  schema, storage

    # 後処理
    # ファイル削除
    os.remove(path)

@pytest.fixture
def create_invalid_test_definition():
    """テスト用のファイルの記載方法が間違っているマッピング定義ファイルを作成します。"""
    # 前処理
    schema = 'test_schema'
    storage = 'test_storage'
    path = f'dg_mm/data/mapping/{storage}_{schema}_mapping.json'
    # ファイル作成
    with open(path, mode='w') as f:
        f.write('dummy text')

    yield schema, storage

    # 後処理
    # ファイル削除
    os.remove(path)

@pytest.fixture
def read_test_mapping_definition():
    """テスト時に用いるマッピング定義を読み込みます。"""

    path = 'tests/models/data/mapping_definition.json'

    with open(path, mode='r') as f:
        data = json.load(f)

    return data

@pytest.fixture
def read_test_expected_schema():
    """テスト実行時に出力が予測されるスキーマを読み込みます。"""

    path = 'tests/models/data/expected_schema.json'

    with open(path, mode='r') as f:
        data = json.load(f)

    return data

@pytest.fixture
def read_test_source_data():
    """テスト時に用いるストレージのソースデータを読み込みます。"""

    path = 'tests/models/data/source_data.json'

    with open(path, mode='r') as f:
        data = json.load(f)

    return data
