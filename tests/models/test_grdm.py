import json
from unittest.mock import Mock

import pytest
import requests

from dg_mm.models.grdm import GrdmAccess
from dg_mm.errors import (
    InvalidTokenError,
    AccessDeniedError,
    APIError,
    InvalidProjectError,
    UnauthorizedError
)


def create_mock_response(code, body = None):
    response = requests.models.Response()
    response.status_code = code
    response.json = Mock(return_value=body)
    return response


def read_json(path):
    with open(path, mode='r') as f:
        return json.load(f)


@pytest.fixture
def authorized_grdm_access():
    instance = GrdmAccess()
    instance._token = "valid_token"
    instance._project_id = "valid_project_id"
    instance._is_authenticated = True
    return instance


@pytest.fixture
def mock_check_token_valid(mocker):
    return mocker.patch('dg_mm.models.grdm.GrdmAccess._check_token_valid')


@pytest.fixture
def mock_check_project_id_valid(mocker):
    return mocker.patch('dg_mm.models.grdm.GrdmAccess._check_project_id_valid')

class TestGrdmAccess():
    def test_check_authentication_success_1(self, mocker, mock_check_token_valid, mock_check_project_id_valid):
        # モック化
        # mocker.patch('dg_mm.models.grdm.GrdmAccess._check_token_valid', return_value=True)
        # mocker.patch('dg_mm.models.grdm.GrdmAccess._check_project_id_valid', return_value=True)
        mock_check_token_valid.return_value = True
        mock_check_project_id_valid.return_value = True

        # テスト実行
        target_class = GrdmAccess()
        valid_token ="valid_token"
        valid_project_id = "valid_project_id"

        actual = target_class.check_authentication(valid_token, valid_project_id)

        # 結果の確認
        assert actual == True
        assert target_class._is_authenticated == True
        assert target_class._token == valid_token
        assert target_class._project_id == valid_project_id

    def test_check_authentication_failure_1(self, mocker):
        # モック化
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_token_valid', return_value=False)
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_project_id_valid', return_value=True)

        # テスト実行
        target_class = GrdmAccess()
        invalid_token ="invalid_token"
        valid_project_id = "valid_project_id"

        actual = target_class.check_authentication(invalid_token, valid_project_id)

        # 結果の確認
        assert actual == False
        assert target_class._is_authenticated == False

    def test_check_authentication_failure_2(self, mocker):
        # モック化
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_token_valid', return_value=True)
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_project_id_valid', return_value=False)

        # テスト実行
        target_class = GrdmAccess()
        valid_token ="valid_token"
        invalid_project_id = "invalid_project_id"

        actual = target_class.check_authentication(valid_token, invalid_project_id)

        # 結果の確認
        assert actual == False
        assert target_class._is_authenticated == False

    def test__check_token_valid_success_1(self, mocker):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_profile_1.json')
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"

        actual = target_class._check_token_valid()

        # 結果の確認
        assert actual == True

    def test__check_token_valid_failure_1(self, mocker):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(401))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(InvalidTokenError, match="認証に失敗しました"):
            target_class._check_token_valid()

    def test__check_token_valid_failure_2(self, mocker):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_profile_2.json')
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(AccessDeniedError, match="トークンのアクセス権が不足しています"):
            target_class._check_token_valid()

    def test__check_token_valid_failure_3(self, mocker):
        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"

        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            target_class._check_token_valid()

    def test__check_token_valid_failure_4(self, mocker):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            target_class._check_token_valid()

    def test__check_project_id_valid_success_1(self, mocker):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_node_1.json')
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "valid_project_id"

        actual = target_class._check_project_id_valid()

        # 結果の確認
        assert actual == True

    def test__check_project_id_valid_failure_1(self, mocker):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(404))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "invalid_project_id"

        with pytest.raises(InvalidProjectError, match="プロジェクトが存在しません"):
            target_class._check_project_id_valid()

    def test__check_project_id_valid_failure_2(self, mocker):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(403))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "invalid_project_id"

        with pytest.raises(AccessDeniedError, match="プロジェクトへのアクセス権がありません"):
            target_class._check_project_id_valid()

    def test__check_project_id_valid_failure_3(self, mocker):
        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "valid_project_id"

        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            target_class._check_project_id_valid()

    def test_get_project_metadata_success_1(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_1.json')  # プロジェクトメタデータが1件登録されている場合のレスポンス
        mock_obj = mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_project_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 1
        assert mock_obj.call_count == 1

    def test_get_project_metadata_success_2(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_2.json')  # プロジェクトメタデータが2件登録されている場合のレスポンス
        mock_obj = mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_project_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 2
        assert mock_obj.call_count == 1

    def test_get_project_metadata_success_3(self, mocker, authorized_grdm_access):
        # モック化
        res_body1 = read_json('tests/models/data/grdm_api_registrations_3.json')    # プロジェクトメタデータが11件登録されている場合の1回目のレスポンス
        res_body2 = read_json('tests/models/data/grdm_api_registrations_4.json')    # プロジェクトメタデータが11件登録されている場合の2回目のレスポンス
        res1 = create_mock_response(200, res_body1)
        res2 = create_mock_response(200, res_body2)
        mock_obj = mocker.patch('requests.get', side_effect=[res1, res2])

        # テスト実行
        actual = authorized_grdm_access.get_project_metadata()

        # 結果の確認
        expected = read_json('tests/models/data/grdm_api_registrations_5.json') # dataが11件のデータ
        assert actual == expected
        assert len(actual["data"]) == 11
        assert mock_obj.call_count == 2

    def test_get_project_metadata_success_4(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_6.json')  # プロジェクトメタデータが登録されていない場合のレスポンス
        mock_obj = mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_project_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 0
        assert mock_obj.call_count == 1

    def test_get_project_metadata_failure_1(self):
        # テスト実行
        target_class = GrdmAccess()

        with pytest.raises(UnauthorizedError, match="認証されていません"):
            target_class.get_project_metadata()

    def test_get_project_metadata_failure_2(self, mocker, authorized_grdm_access):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            authorized_grdm_access.get_project_metadata()

    def test_get_project_metadata_failure_3(self, mocker, authorized_grdm_access):
        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            authorized_grdm_access.get_project_metadata()

    def test_get_file_metadata_1(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_1.json')  # ファイルメタデータが1件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_file_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]["attributes"]["files"]) == 1

    def test_get_file_metadata_2(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_2.json')  # ファイルメタデータが2件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_file_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]["attributes"]["files"]) == 2

    def test_get_file_metadata_3(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_3.json')  # ファイルメタデータが登録されていない場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_file_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]["attributes"]["files"]) == 0

    def test_get_file_metadata_4(self, mocker, authorized_grdm_access):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(400))

        # テスト実行
        actual = authorized_grdm_access.get_file_metadata()

        # 結果の確認
        assert actual == {}

    def test_get_file_metadata_failure_1(self):
        # テスト実行
        target_class = GrdmAccess()

        with pytest.raises(UnauthorizedError, match="認証されていません"):
            target_class.get_file_metadata()

    def test_get_file_metadata_failure_2(self, mocker, authorized_grdm_access):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            authorized_grdm_access.get_file_metadata()

    def test_get_file_metadata_failure_3(self, mocker, authorized_grdm_access):
        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            authorized_grdm_access.get_file_metadata()

    def test_get_project_info_success_1(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_3.json')  # プロジェクト情報の正常なレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_project_info()

        # 結果の確認
        assert actual == api_res

    def test_get_project_info_failure_1(self):
        # テスト実行
        target_class = GrdmAccess()

        with pytest.raises(UnauthorizedError, match="認証されていません"):
            target_class.get_project_info()

    def test_get_project_info_failure_2(self, mocker, authorized_grdm_access):
        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            authorized_grdm_access.get_project_info()

    def test_get_project_info_failure_3(self, mocker, authorized_grdm_access):
        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            authorized_grdm_access.get_project_info()

    def test_get_member_info_1(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_contributors_1.json')  # メンバー情報が１件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_member_info()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 1

    def test_get_member_info_2(self, mocker, authorized_grdm_access):
        # モック化
        api_res = read_json('tests/models/data/grdm_api_contributors_2.json')  # メンバー情報が2件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        actual = authorized_grdm_access.get_member_info()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 2

    def test_get_member_info_3(self, mocker, authorized_grdm_access):
        # モック化
        api_res1 = read_json('tests/models/data/grdm_api_contributors_3.json')  # メンバー情報が11件登録されている場合の1回目のレスポンス
        api_res2 = read_json('tests/models/data/grdm_api_contributors_4.json')  # メンバー情報が11件登録されている場合の2回目のレスポンス
        res1 = create_mock_response(200, api_res1)
        res2 = create_mock_response(200, api_res2)
        mock_obj = mocker.patch('requests.get', side_effext=[res1, res2])

        # テスト実行
        actual = authorized_grdm_access.get_member_info()

        # 結果の確認
        assert len(actual["data"]) == 11
        assert mock_obj.call_count == 2