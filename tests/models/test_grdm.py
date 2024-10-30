import json
import pytest
import requests
from unittest.mock import Mock


from dg_mm.models.grdm import GrdmAccess
from dg_mm.errors import (
    InvalidTokenError,
    AccessDeniedError,
    APIError,
    InvalidIdError,
    MetadataNotFoundError,
    UnauthorizedError
)


def create_mock_response(code, body=None):
    response = requests.models.Response()
    response.status_code = code
    response.json = Mock(return_value=body)
    return response


def read_json(path):
    with open(path, mode='r') as f:
        return json.load(f)


def create_authorized_grdm_access():
    instance = GrdmAccess()
    instance._token = "valid_token"
    instance._project_id = "valid_project_id"
    instance._is_authenticated = True
    return instance


class TestGrdmAccess():
    def test_check_authentication_success_1(self, mocker):
        """すべてのチェックOKの時に認証成功となる"""

        # モック化
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_token_valid', return_value=True)
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_project_id_valid', return_value=True)

        # テスト実行
        target_class = GrdmAccess()
        valid_token = "valid_token"
        valid_project_id = "valid_project_id"

        actual = target_class.check_authentication(valid_token, valid_project_id)

        # 結果の確認
        assert actual == True
        assert target_class._is_authenticated == True
        assert target_class._token == valid_token
        assert target_class._project_id == valid_project_id

    def test_check_authentication_failure_1(self, mocker):
        """トークンの認証に失敗"""

        # モック化
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_token_valid', return_value=False)
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_project_id_valid', return_value=True)

        # テスト実行
        target_class = GrdmAccess()
        invalid_token = "invalid_token"
        valid_project_id = "valid_project_id"

        actual = target_class.check_authentication(invalid_token, valid_project_id)

        # 結果の確認
        assert actual == False
        assert target_class._is_authenticated == False

    def test_check_authentication_failure_2(self, mocker):
        """プロジェクトの認証に失敗"""

        # モック化
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_token_valid', return_value=True)
        mocker.patch('dg_mm.models.grdm.GrdmAccess._check_project_id_valid', return_value=False)

        # テスト実行
        target_class = GrdmAccess()
        valid_token = "valid_token"
        invalid_project_id = "invalid_project_id"

        actual = target_class.check_authentication(valid_token, invalid_project_id)

        # 結果の確認
        assert actual == False
        assert target_class._is_authenticated == False

    def test__check_token_valid_success_1(self, mocker):
        """チェックOKの時に認証成功となる"""

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
        """トークンが存在しない"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(401))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(InvalidTokenError, match="認証に失敗しました"):
            target_class._check_token_valid()

    def test__check_token_valid_failure_2(self, mocker):
        """トークンのアクセス権がない"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_profile_2.json')
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(AccessDeniedError, match="トークンのアクセス権が不足しています"):
            target_class._check_token_valid()

    def test__check_token_valid_failure_3(self, mocker):
        """APIのレスポンスが返らず、タイムアウトする"""

        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"

        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            target_class._check_token_valid()

    def test__check_token_valid_failure_4(self, mocker):
        """APIエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            target_class._check_token_valid()

    def test__check_project_id_valid_success_1(self, mocker):
        """チェックOKの時に認証成功となる"""

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
        """プロジェクトが存在しない"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(404))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "invalid_project_id"

        with pytest.raises(InvalidIdError, match="プロジェクトが存在しません"):
            target_class._check_project_id_valid()

    def test__check_project_id_valid_failure_2(self, mocker):
        """トークンを発行したユーザーにプロジェクトのアクセス権がない"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(403))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "invalid_project_id"

        with pytest.raises(AccessDeniedError, match="プロジェクトへのアクセス権がありません"):
            target_class._check_project_id_valid()

    def test__check_project_id_valid_failure_3(self, mocker):
        """APIのレスポンスが返らず、タイムアウトする"""

        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "valid_project_id"

        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            target_class._check_project_id_valid()

    def test_get_project_metadata_success_1(self, mocker):
        """プロジェクトメタデータが登録されている場合にメタデータが取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_1.json')  # プロジェクトメタデータが1件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_project_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 1

    def test_get_project_metadata_success_2(self, mocker):
        """プロジェクトメタデータが複数登録されている場合にメタデータが取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_2.json')  # プロジェクトメタデータが2件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_project_metadata()

        # 結果の確認
        assert len(actual["data"]) == 1
        assert actual["data"][0] == api_res["data"][0]

    def test_get_project_metadata_success_3(self, mocker):
        """プロジェクトメタデータが登録されていない場合にエラーにならない"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_3.json')  # プロジェクトメタデータが登録されていない場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_project_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 0

    def test_get_project_metadata_success_4(self, mocker):
        """プロジェクトメタデータのIDを指定して、プロジェクトメタデータが取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_1.json')  # 指定したIDのプロジェクトメタデータが存在する場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_project_metadata(project_metadata_id="valid")

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 1

    def test_get_project_metadata_failure_1(self, mocker):
        """指定したプロジェクトメタデータIDが存在しない"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_3.json')  # 指定したIDのプロジェクトメタデータが存在しない場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(MetadataNotFoundError, match="指定したIDのプロジェクトメタデータが存在しません"):
            instance.get_project_metadata(project_metadata_id="invalid")

    def test_get_project_metadata_failure_2(self, mocker):
        """別のプロジェクトが持つプロジェクトメタデータIDを指定"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_4.json')  # 別のプロジェクトのメタデータIDを指定した場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(MetadataNotFoundError, match="指定したIDのプロジェクトメタデータが存在しません"):
            instance.get_project_metadata(project_metadata_id="invalid")

    def test_get_project_metadata_failure_3(self):
        """認証前に関数実行"""

        # テスト実行
        target_class = GrdmAccess()

        with pytest.raises(UnauthorizedError, match="認証されていません"):
            target_class.get_project_metadata()

    def test_get_project_metadata_failure_4(self, mocker):
        """APIエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            instance.get_project_metadata()

    def test_get_project_metadata_failure_5(self, mocker):
        """APIのレスポンスが返らず、タイムアウトする"""

        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            instance.get_project_metadata()

    def test_get_file_metadata_1(self, mocker):
        """ファイルメタデータが登録されている場合にメタデータが取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_1.json')  # ファイルメタデータが1件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_file_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]["attributes"]["files"]) == 1

    def test_get_file_metadata_2(self, mocker):
        """ファイルメタデータが複数登録されている場合にメタデータが取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_2.json')  # ファイルメタデータが2件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_file_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]["attributes"]["files"]) == 2

    def test_get_file_metadata_3(self, mocker):
        """ファイルメタデータが登録されていない場合にエラーにならない"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_3.json')  # ファイルメタデータが登録されていない場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_file_metadata()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]["attributes"]["files"]) == 0

    def test_get_file_metadata_4(self, mocker):
        """GRDM上でメタデータのアドオンが無効の場合でもエラーにならない"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(400))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_file_metadata()

        # 結果の確認
        assert actual == {}

    def test_get_file_metadata_failure_1(self):
        """認証前に関数実行"""

        # テスト実行
        target_class = GrdmAccess()

        with pytest.raises(UnauthorizedError, match="認証されていません"):
            target_class.get_file_metadata()

    def test_get_file_metadata_failure_2(self, mocker):
        """APIエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            instance.get_file_metadata()

    def test_get_file_metadata_failure_3(self, mocker):
        """APIのレスポンスが返らず、タイムアウトする"""

        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            instance.get_file_metadata()

    def test_get_project_info_success_1(self, mocker):
        """プロジェクト情報が取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_file_metadata_3.json')  # プロジェクト情報の正常なレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_project_info()

        # 結果の確認
        assert actual == api_res

    def test_get_project_info_failure_1(self):
        """認証前に関数実行"""

        # テスト実行
        target_class = GrdmAccess()

        with pytest.raises(UnauthorizedError, match="認証されていません"):
            target_class.get_project_info()

    def test_get_project_info_failure_2(self, mocker):
        """APIエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            instance.get_project_info()

    def test_get_project_info_failure_3(self, mocker):
        """APIのレスポンスが返らず、タイムアウトする"""

        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            instance.get_project_info()

    def test_get_member_info_1(self, mocker):
        """メンバー情報が取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_contributors_1.json')  # メンバー情報が１件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_member_info()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 1

    def test_get_member_info_2(self, mocker):
        """複数メンバーが登録されているプロジェクトでメンバー情報が取得できる"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_contributors_2.json')  # メンバー情報が2件登録されている場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_member_info()

        # 結果の確認
        assert actual == api_res
        assert len(actual["data"]) == 2

    def test_get_member_info_3(self, mocker):
        """メンバー数がAPIで1回に取得できる数より多い場合でも全件取得できる"""

        # モック化
        api_res1 = read_json('tests/models/data/grdm_api_contributors_3.json')  # メンバー情報が11件登録されている場合の1回目のレスポンス
        api_res2 = read_json('tests/models/data/grdm_api_contributors_4.json')  # メンバー情報が11件登録されている場合の2回目のレスポンス
        res1 = create_mock_response(200, api_res1)
        res2 = create_mock_response(200, api_res2)
        mock_obj = mocker.patch('requests.get', side_effect=[res1, res2])

        # テスト実行
        instance = create_authorized_grdm_access()
        actual = instance.get_member_info()

        # 結果の確認
        assert len(actual["data"]) == 11
        assert mock_obj.call_count == 2

    def test_get_member_info_failure_1(self):
        """認証前に関数実行"""

        # テスト実行
        target_class = GrdmAccess()

        with pytest.raises(UnauthorizedError, match="認証されていません"):
            target_class.get_member_info()

    def test_get_member_info_failure_2(self, mocker):
        """APIエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            instance.get_member_info()

    def test_get_member_info_failure_3(self, mocker):
        """APIのレスポンスが返らず、タイムアウトする"""

        # モック化
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(APIError, match="APIリクエストがタイムアウトしました"):
            instance.get_member_info()
