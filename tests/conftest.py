import configparser
import json
import os
import pytest


@pytest.fixture
def create_dummy_file():
    path = 'dg_mm/data/exist.txt'

    # ファイル作成
    with open(path, mode='w') as f:
        f.write('dummy text')

    yield {
        'file': 'data/exist.txt',
        'dir': 'data',
        'not_exist': 'data/not_exist.txt',
    }

    # ファイル削除
    os.remove(path)


@pytest.fixture
def create_dummy_json():
    path = 'dg_mm/data/dummy.json'
    relative_path = 'data/dummy.json'

    # ファイル作成
    contents = {
        'key1': 'value1'
    }
    with open(path, 'w') as f:
        json.dump(contents, f)

    yield relative_path

    # ファイル削除
    os.remove(path)


@pytest.fixture
def create_dummy_ini():
    path = 'dg_mm/data/dummy.ini'
    relative_path = 'data/dummy.ini'

    # ファイル作成
    config = configparser.ConfigParser()
    config['section1'] = {'key1': 'value1'}
    with open(path, 'w') as f:
        config.write(f)

    yield relative_path

    # ファイル削除
    os.remove(path)
