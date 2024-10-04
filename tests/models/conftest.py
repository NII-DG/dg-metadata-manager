import os
import pytest


@pytest.fixture
def create_dummy_definition():
    # 前処理
    schema = 'dummy'
    storage = 'dummy'
    path = f'dg_mm/data/mapping/{schema}-{storage}-mapping.json'
    # ファイル作成
    with open(path, mode='w') as f:
        f.write('dummy text')

    yield {
        'schema': schema,
        'storage': storage,
    }

    # 後処理
    # ファイル削除
    os.remove(path)