import json

from dg_mm.models.grdm import GrdmAccess


class MockResponse():
    def __init__(self, code, body=None):
        self.code = code
        self.body = body

    def json(self):
        return self.body

    @property
    def status_code(self):
        return self.code


def read_json(path):
    with open(path, mode='r') as f:
        return json.load(f)


class TestGrdmAccess():
    def test__check_token_valid_1(self, mocker):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_profile_1.json')
        mocker.patch('requests.get', return_value=MockResponse(200, api_res))

        # テスト実行
        target_class = GrdmAccess()
        actual = target_class._check_token_valid()

        # 結果の確認
        assert actual == True
