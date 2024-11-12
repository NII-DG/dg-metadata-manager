"""grdm.pyをテストするためのモジュールです。"""
import json
import pytest
import requests
from multiprocessing import AuthenticationError
from typing import Counter
from unittest.mock import Mock


from dg_mm.models.grdm import GrdmAccess, GrdmMapping
from dg_mm.errors import (
    MappingDefinitionNotFoundError,
    InvalidSchemaError,
    InvalidTokenError,
    AccessDeniedError,
    APIError,
    InvalidIdError,
    MetadataNotFoundError,
    UnauthorizedError,
    DataFormatError,
    MappingDefinitionError,
    DataTypeError,
    KeyNotFoundError,
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


class TestGrdmMapping():
    """GrdmMappingクラスをテストするためのクラスです。"""

    def test_mapping_metadata_1(self, mocker, read_test_mapping_definition, read_test_expected_schema):
        """(正常系テスト 4)スキーマ全体のメタデータを取得する場合のテストケースです。"""

        metadata_sources = ["member_info"]
        source_data = {"key": "value1"}

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_1"]
        expected_new_schema = read_test_expected_schema["test_mapping_metadata_1"]

        # _mapping_metadata内で呼び出す各関数をモック化
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", return_value=expected_new_schema)
        mock__add_unmap_property = mocker.patch("dg_mm.models.grdm.GrdmMapping._add_unmap_property", return_value=expected_new_schema)

        # テスト実施
        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        # 戻り値が期待通りかの検証
        assert metadata == expected_new_schema
        # モック化した各関数が想定された数だけ呼び出されているかの検証
        assert mock__extract_and_insert_metadata.call_count == 2
        assert mock__add_unmap_property.call_count == 1
        # 各プロパティが正確に処理されているかの検証
        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[0][0][2]
        assert schema_property_arg == "sc1[].sc2[]"
        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[1][0][2]
        assert schema_property_arg == "sc1[].sc3[].sc5"
        schema_properties_arg = mock__add_unmap_property.call_args_list[0][0][1]
        assert schema_properties_arg == ["sc1[]", "sc3[]", "sc4[]"]

    def test_mapping_metadata_2(self, mocker, read_test_mapping_definition, read_test_expected_schema):
        """(正常系テスト 5)filter_propertiesで指定されたプロパティのメタデータのみを取得する場合のテストケースです。"""

        filter_properties = ["sc1.sc2", "sc1.sc3.sc5"]
        metadata_sources = ["project_info", "member_info"]
        source_data = {"key": "value1"}

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_2"]
        expected_new_schema = read_test_expected_schema["test_mapping_metadata_2"]

        # _mapping_metadata内で呼び出す各関数をモック化
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mock_get_project_info = mocker.patch("dg_mm.models.grdm.GrdmAccess.get_project_info", return_value=source_data)
        mock_get_member_info = mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", return_value=expected_new_schema)

        # テスト実施
        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata("RF", "valid_token", "valid_project_id", filter_properties)

        # 戻り値が期待通りかの検証
        assert metadata == expected_new_schema
        # モック化した各関数が想定された数だけ呼び出されているかの検証
        assert mock_get_project_info.call_count == 1
        assert mock_get_member_info.call_count == 1
        assert mock__extract_and_insert_metadata.call_count == 2
        # 各プロパティが正確に処理されているかの検証
        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[0][0][2]
        assert schema_property_arg == "sc1[].sc2[]"
        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[1][0][2]
        assert schema_property_arg == "sc1[].sc3[].sc5"

    def test_mapping_metadata_3(self, mocker, read_test_mapping_definition, read_test_expected_schema):
        """(正常系テスト 6)filter_propertiesで指定されたすべてのプロパティに対応するメタデータが存在しない場合のテストケースです。"""

        metadata_sources = []

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_3"]
        expected_new_schema = read_test_expected_schema["test_mapping_metadata_3"]

        # _mapping_metadata内で呼び出す各関数をモック化
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mock__add_property = mocker.patch("dg_mm.models.grdm.GrdmMapping._add_property", return_value=expected_new_schema)

        # テスト実施
        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        # 戻り値が期待通りかの検証
        assert metadata == expected_new_schema
        # モック化した各関数が想定された数だけ呼び出されているかの検証
        assert mock__add_property.call_count == 0

    def test_mapping_metadata_4(self, mocker):
        """(異常系テスト 7)GRDMの認証に失敗した場合のテストケースです。"""

        error_message = "dummy message"

        # 認証を行う関数が呼ばれた際にエラーを返すようにモック化
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication", side_effect=AuthenticationError(error_message))

        with pytest.raises(AuthenticationError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "invalid_token", "invalid_project_id")

        assert str(e.value) == error_message

    def test_mapping_metadata_5(self, mocker):
        """(異常系テスト 8)マッピング定義ファイルの読み込みに失敗した場合のテストケースです。"""

        error_message = "dummy message"

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=MappingDefinitionError(error_message))

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "invalid_token", "invalid_project_id")

        assert str(e.value) == error_message

    def test_mapping_metadata_6(self, mocker):
        """(異常系テスト 9)filter_properties(取得するプロパティ一覧)が空の場合のテストケースです。"""

        error_message = "dummy message"
        filter_properties = []

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=KeyNotFoundError(error_message))

        with pytest.raises(KeyNotFoundError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "invalid_token", "invalid_project_id", filter_properties)

        assert str(e.value) == error_message

    def test_mapping_metadata_7(self, mocker):
        """(異常系テスト 10)filter_propertiesとして存在しないプロパティが指定された場合のテストケースです。"""

        error_message = "dummy message"
        filter_properties = ["non_existent_property"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=KeyNotFoundError(error_message))

        with pytest.raises(KeyNotFoundError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "invalid_token", "invalid_project_id", filter_properties)

        assert str(e.value) == error_message

    def test_mapping_metadata_8(self, mocker):
        """(異常系テスト 11)metadata_sourcesに存在する取得先からのメタデータの取得に失敗した場合のテストケースです。"""

        error_message = "dummy message"
        metadata_sources = ["project_info", "member_info", "project_metadata", "file_metadata"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition")
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_project_info", side_effect=APIError(error_message))

        with pytest.raises(Exception) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "invalid_token", "invalid_project_id")

        assert str(e.value) == error_message

    def test_mapping_metadata_9(self, mocker, read_test_mapping_definition):
        """(異常系テスト 12)マッピングに失敗した場合のエラーケースです。"""

        error_message = "dummy message"
        metadata_sources = ["member_info"]
        source_data = {"key": "value"}

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_1"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=MappingDefinitionError(error_message))

        with pytest.raises(MappingDefinitionError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 1
        assert str(e.value) == error_message

    def test_mapping_metadata_10(self, mocker):
        """(異常系テスト)_find_metadata_sourcesで特定した取得先の中にGRDMに存在しない取得先が含まれていた場合のテストケースです。"""

        test_mapping_definition = {}
        metadata_sources = ["project_info", "non_existent_info", "file_metadata", "non_existent_metadata"]
        error_sources = ["non_existent_info", "non_existent_metadata"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mock_get_project_info = mocker.patch("dg_mm.models.grdm.GrdmAccess.get_project_info")
        mock_get_file_matadata = mocker.patch("dg_mm.models.grdm.GrdmAccess.get_file_metadata")

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        assert mock_get_project_info.call_count == 1
        assert mock_get_file_matadata.call_count == 1
        assert str(e.value) == f"メタデータ取得先:{error_sources}が存在しません。"

    def test_mapping_metadata_11(self, mocker, read_test_mapping_definition):
        """(異常系テスト)一致するストレージのキーが存在しない場合のテストケースです。"""

        metadata_sources = ["member_info"]
        source_data = {"key": "value"}
        error_message1 = "st1と一致するストレージのキーが見つかりませんでした。(sc1[].sc2[])"
        error_message2 = "st2と一致するストレージのキーが見つかりませんでした。(sc1[].sc3.sc4)"
        errors = [
            KeyNotFoundError([error_message1]),
            KeyNotFoundError([error_message2]),
        ]

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_11"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=errors)

        with pytest.raises(KeyNotFoundError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 2
        assert str(e.value) == f"キーの不一致が確認されました。:['{error_message1}', '{error_message2}']"

    def test_mapping_metadata_12(self, mocker, read_test_mapping_definition):
        """(異常系テスト)データの型変換に失敗した場合のテストケースです。"""

        metadata_sources = ["member_info"]
        source_data = {"key": "value"}
        error_message1 = "型変換エラー：storage_dataをbooleanに変換できません。(sc1[].sc2[])"
        error_message2 = "型変換エラー：storage_dataをnumberに変換できません。(sc1[].sc3.sc4)"
        errors = [
            DataTypeError(error_message1),
            DataTypeError(error_message2),
        ]

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_11"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=errors)

        with pytest.raises(DataTypeError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 2
        assert str(e.value) == f"データの変換に失敗しました。：['{error_message1}', '{error_message2}']"

    def test_mapping_metadata_13(self, mocker, read_test_mapping_definition):
        """(異常系テスト)ストレージのキーが一致しないエラーとデータの型変換に失敗したエラーの両方が発生した場合のテストケースです。"""

        metadata_sources = ["member_info"]
        source_data = {"key": "value"}
        error_message1 = "st1と一致するストレージのキーが見つかりませんでした。(sc1[].sc2[])"
        error_message2 = "型変換エラー：storage_dataをnumberに変換できません。(sc1[].sc3.sc4)"
        errors = [
            KeyNotFoundError([error_message1]),
            DataTypeError(error_message2),
        ]

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_11"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=errors)

        with pytest.raises(DataFormatError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 2
        assert str(e.value) == f"キーの不一致が確認されました。:['{error_message1}'], データの変換に失敗しました。：['{error_message2}']"

    def test_mapping_metadata_14(self, mocker):
        """(異常系テスト)存在しないスキーマを指定した場合のテストケースです。"""

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=MappingDefinitionNotFoundError())

        with pytest.raises(InvalidSchemaError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("dummy", "invalid_token", "invalid_project_id")

        assert str(e.value) == "対応していないスキーマが指定されました。"

    def test_mapping_metadata_15(self, mocker, read_test_mapping_definition, read_test_new_schema):
        """(異常系テスト)マッピング先がないプロパティとマッピング先があるプロパティのスキーマ定義に差異があった場合のテストケースです。"""

        metadata_sources = ["member_info"]
        source_data = {"key": "value1"}

        test_mapping_definition = read_test_mapping_definition["test_mapping_metadata_15"]
        new_schema = read_test_new_schema["test_mapping_metadata_15"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", return_value=new_schema)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._add_unmap_property", side_effect=MappingDefinitionError())

        # テスト実施
        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("RF", "valid_token", "valid_project_id")

        assert str(e.value) == "データ構造が定義と異なっています。(sc1[].sc3[].sc4[])"

    def test__find_metadata_sources_1(self, read_test_mapping_definition):
        """(正常系テスト 7)マッピング定義にある全取得先を取得する場合のテストケースです。"""

        expected_metadata_sources = ["project_info", "member_info"]

        test_mapping_definition = read_test_mapping_definition["test__find_metadata_sources_1"]

        target_class = GrdmMapping()
        # インスタンス変数にテスト用のマッピング定義を設定
        target_class._mapping_definition = test_mapping_definition

        metadata_sources = target_class._find_metadata_sources()

        assert Counter(metadata_sources) == Counter(expected_metadata_sources)

    def test__find_metadata_sources_2(self, read_test_mapping_definition):
        """(正常系テスト 8)マッピング定義に取得先が一つも存在しない場合のテストケースです。"""

        test_mapping_definition = read_test_mapping_definition["test__find_metadata_sources_2"]

        target_class = GrdmMapping()
        target_class._mapping_definition = test_mapping_definition
        metadata_sources = target_class._find_metadata_sources()

        assert not metadata_sources

    def test__extract_and_insert_metadata_1(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 9)マッピングのテストケースNo.1のテストです。

        データが単一項目同士であり、型も同じ場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_1"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__extract_and_insert_metadata_1"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_1"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_2(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 10)マッピングのテストケースNo.2のテストです。

        データがリスト同士であり、型も同じ場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_2"]
        schema_property = "sc1.sc2[]"
        components = read_test_components["test__extract_and_insert_metadata_2"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_2"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_3(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 11)マッピングのテストケースNo.3のテストです。

        データが単一項目同士であり、型が異なる場合（変換可能）のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_3"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__extract_and_insert_metadata_3"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_3"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_4(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 12)マッピングのテストケースNo.4のテストです。

        データがリスト同士であり、型が異なる場合（変換可能）のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_4"]
        schema_property = "sc1.sc2[]"
        components = read_test_components["test__extract_and_insert_metadata_4"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_4"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_5(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 13)マッピングのテストケースNo.5のテストです。

        ストレージのデータが単一項目でスキーマがリストの場合（型は同じ）のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_5"]
        schema_property = "sc1.sc2[]"
        components = read_test_components["test__extract_and_insert_metadata_5"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_5"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_6(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 14)マッピングのテストケースNo.6のテストです。

        ストレージのデータが単一項目でスキーマがリストの場合（型は異なるが変換可能）のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_6"]
        schema_property = "sc1.sc2[]"
        components = read_test_components["test__extract_and_insert_metadata_6"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_6"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_7(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 15)マッピングのテストケースNo.7のテストです。

        ストレージのデータがリストでスキーマが単一項目の場合（型は同じ）のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_7"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__extract_and_insert_metadata_7"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_7"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_8(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 16)マッピングのテストケースNo.8のテストです。

        ストレージのデータが単一項目でスキーマがリストの場合（型は異なるが変換可能）のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_8"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__extract_and_insert_metadata_8"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_8"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_9(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 17)マッピングのテストケースNo.9のテストです。

        ストレージのデータ内部にリストが含まれており、スキーマに対応するプロパティが存在する場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_9"]
        schema_property = "sc1[].sc2"
        components = read_test_components["test__extract_and_insert_metadata_9"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_9"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_10(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 18)マッピングのテストケースNo.10のテストです。

        スキーマの内部にリストが存在するが、対応する項目がストレージに存在しない場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_10"]
        schema_property = "sc1[].sc2"
        components = read_test_components["test__extract_and_insert_metadata_10"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_10"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_11(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 19)マッピングのテストケースNo.11のテストです。

        ストレージのデータ内部にリストが含まれているが、スキーマに対応するプロパティが存在しない場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_11"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__extract_and_insert_metadata_11"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_11"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_12(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 20)マッピングのテストケースNo.12のテストです。

        ストレージのデータ内部にリストが複数含まれており、スキーマに対応するプロパティが存在するものとしないものが混在する場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_12"]
        schema_property = "sc1[].sc2.sc3[].sc4"
        components = read_test_components["test__extract_and_insert_metadata_12"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3", "st4"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_12"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_13(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 23)マッピングのテストケースNo.15のテストです。

        ストレージのデータが値の設定されていない単一項目の場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_13"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__extract_and_insert_metadata_13"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_13"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_14(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """(正常系テスト 24)マッピングのテストケースNo.16のテストです。

        ストレージのデータが値の設定されていないリストの場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_14"]
        schema_property = "sc1.sc2[]"
        components = read_test_components["test__extract_and_insert_metadata_14"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        expected_schema = read_test_expected_schema["test__extract_and_insert_metadata_14"]

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == expected_schema

    def test__extract_and_insert_metadata_15(self, read_test_source_data, read_test_components):
        """(異常系テスト 15)マッピングのテストケースNo.17のテストです。

        データが単一項目同士であるが、型が異なり変換が不可能な場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_15"]
        schema_property = "sc1.sc2[]"
        components = read_test_components["test__extract_and_insert_metadata_15"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        target_class = GrdmMapping()
        with pytest.raises(DataTypeError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"型変換エラー：['value1']をnumberに変換できません。({schema_property})"

    def test__extract_and_insert_metadata_16(self, read_test_source_data, read_test_components):
        """(異常系テスト 16)マッピングのテストケースNo.18のテストです。

        データがリスト同士であるが、型が異なり変換が不可能な場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_16"]
        schema_property = "sc1.sc2[]"
        components = read_test_components["test__extract_and_insert_metadata_16"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]

        target_class = GrdmMapping()
        with pytest.raises(DataTypeError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"型変換エラー：['value1', 'value2']をnumberに変換できません。({schema_property})"

    def test__extract_and_insert_metadata_17(self, read_test_new_schema, read_test_source_data, read_test_components):
        """(異常系テスト 17)マッピングのテストケースNo.19のテストです。

        スキーマのプロパティごとにリストの定義が異なっている場合のテストケースです。

        """
        new_schema = read_test_new_schema["test__extract_and_insert_metadata_17"]
        sources = read_test_source_data["test__extract_and_insert_metadata_17"]
        schema_property = "sc1.sc3"
        components = read_test_components["test__extract_and_insert_metadata_17"]
        schema_link_list = {}
        storage_keys = ["st1", "st3"]

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"リスト：st1の定義が不足しています。({schema_property})"

    def test__extract_and_insert_metadata_18(self, read_test_source_data, read_test_components):
        """(異常系テスト 18)マッピングのテストケースNo.20のテストです。

        実際にはリストであるストレージの構造がマッピング定義ではオブジェクトと定義されていた場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_18"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__extract_and_insert_metadata_18"]
        schema_link_list = {}
        storage_keys = ["st1", "st2"]

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"リスト：st1の定義が不足しています。({schema_property})"

    def test__extract_and_insert_metadata_19(self, read_test_source_data, read_test_components):
        """(異常系テスト 19)マッピングのテストケースNo.21のテストです。

        実際にはオブジェクトであるストレージの構造がマッピング定義ではリストと定義されていた場合のテストケースです。

        """
        new_schema = {}
        sources = read_test_source_data["test__extract_and_insert_metadata_19"]
        schema_property = "sc1[].sc2"
        components = read_test_components["test__extract_and_insert_metadata_19"]
        schema_link_list = {}
        storage_keys = ["st1", "st2"]

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"オブジェクト：st1がリストとして定義されています。({schema_property})"

    def test__extract_and_insert_metadata_20(self, read_test_new_schema, read_test_source_data, read_test_components):
        """(異常系テスト 20)マッピングのテストケースNo.22のテストです。

        プロパティごとにリストの対応付けが異なっている場合のテストケースです。

        """
        new_schema = read_test_new_schema["test__extract_and_insert_metadata_20"]
        sources = read_test_source_data["test__extract_and_insert_metadata_20"]
        schema_property = "sc1[].sc2.sc3[].sc5"
        components = read_test_components["test__extract_and_insert_metadata_20"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3", "st5"]

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"マッピング定義に誤りがあります。({schema_property})"

    def test__check_and_handle_key_structure_1(self, read_test_source_data, read_test_components):
        """（異常系テスト）ストレージに一致するキーが存在しなかった場合のテストケースです。"""

        new_schema = {}
        sources = read_test_source_data["test__check_and_handle_key_structure_1"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__check_and_handle_key_structure_1"]
        schema_link_list = {}
        storage_keys = ["st0", "st2"]
        index = 0
        key = "st0"

        target_class = GrdmMapping()
        with pytest.raises(KeyNotFoundError) as e:
            new_schema = target_class._check_and_handle_key_structure(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert str(e.value) == f"st0と一致するストレージのキーが見つかりませんでした。({schema_property})"

    def test__check_and_handle_key_structure_2(self, read_test_source_data, read_test_components):
        """（異常系テスト）ストレージにキーが不足していた場合のテストケースです。"""

        new_schema = {}
        sources = read_test_source_data["test__check_and_handle_key_structure_2"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__check_and_handle_key_structure_2"]
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
        index = 0
        key = "st1"

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._check_and_handle_key_structure(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert str(e.value) == f"データ構造が定義と異なっています。({schema_property})"

    def test__handle_list_1(self, read_test_source_data, read_test_components):
        """（異常系テスト）リスト内のオブジェクトに期待されるキーが存在しないものが含まれる場合のテストケースです。"""

        new_schema = {}
        sources = read_test_source_data["test__handle_list_1"]
        schema_property = "sc1[].sc2.sc3"
        components = read_test_components["test__handle_list_1"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        index = 0
        key = "st1"

        target_class = GrdmMapping()
        with pytest.raises(KeyNotFoundError) as e:
            target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert e.value.args[0] == [f"st2と一致するストレージのキーが見つかりませんでした。({schema_property})"]

    def test__handle_list_2(self, read_test_source_data, read_test_components):
        """（異常系テスト）異なる複数のリスト内にキーが存在しないオブジェクトが存在する場合のテストケースです。"""

        new_schema = {}
        sources = read_test_source_data["test__handle_list_2"]
        schema_property = "sc1[].sc2[].sc3"
        components = read_test_components["test__handle_list_2"]
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3", "st4"]
        index = 0
        key = "st1"

        with pytest.raises(KeyNotFoundError) as e:
            target_class = GrdmMapping()
            target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert e.value.args[0] == [f"st2と一致するストレージのキーが見つかりませんでした。({schema_property})",
                                   f"st3と一致するストレージのキーが見つかりませんでした。({schema_property})"]

    def test__handle_list_3(self, read_test_source_data, read_test_components):
        """（異常系テスト）マッピング定義の'list'で指定されたインデックスに対応するデータがストレージに存在しない場合のテストケースです。"""

        new_schema = {}
        sources = read_test_source_data["test__handle_list_3"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__handle_list_3"]
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
        index = 0
        key = "st1"

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert str(e.value) == f"listで指定されたインデックス:2が存在しません。({schema_property})"

    def test__get_and_insert_final_key_value_1(self, read_test_components, read_test_expected_schema):
        """（正常系テスト）末端のキーが存在しない場合のテストケースです。"""

        new_schema = {}
        source = {}
        schema_property = "sc1.sc2"
        components = read_test_components["test__get_and_insert_final_key_value_1"]
        final_key = "st2"
        schema_link_list = {}

        expected_schema = read_test_expected_schema["test__get_and_insert_final_key_value_1"]

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert new_schema == expected_schema

    def test__get_and_insert_final_key_value_2(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """（正常系テスト）末端のキーがリストであり、その値と対応するリストが存在する場合のテストケースです。"""

        new_schema = {}
        source = read_test_source_data["test__get_and_insert_final_key_value_2"]
        schema_property = "sc1[].sc2"
        components = read_test_components["test__get_and_insert_final_key_value_2"]
        final_key = "st2"
        schema_link_list = {}

        expected_schema = read_test_expected_schema["test__get_and_insert_final_key_value_2"]

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert new_schema == expected_schema

    def test__get_and_insert_final_key_value_3(self, read_test_source_data, read_test_components, read_test_expected_schema):
        """（正常系テスト）末端のキーがリストであり、その値と対応するリストが存在しない場合のテストケースです。"""

        new_schema = {}
        source = read_test_source_data["test__get_and_insert_final_key_value_3"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__get_and_insert_final_key_value_3"]
        final_key = "st2"
        schema_link_list = {}

        expected_schema = read_test_expected_schema["test__get_and_insert_final_key_value_3"]

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert new_schema == expected_schema

    def test__get_and_insert_final_key_value_4(self, read_test_source_data, read_test_components):
        """（異常系テスト）'list'に記載された末端のキーのリストのインデックスと対応するデータが存在しない場合のテストケースです。"""

        new_schema = {}
        source = read_test_source_data["test__get_and_insert_final_key_value_4"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__get_and_insert_final_key_value_4"]
        final_key = "st2"
        schema_link_list = {}

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert str(e.value) == f"listで指定されたインデックスが存在しません。({schema_property})"

    def test__get_and_insert_final_key_value_5(self, read_test_source_data, read_test_components):
        """（異常系テスト）マッピング定義に記載されているストレージのキーが不足している場合のテストケースです。"""

        new_schema = {}
        source = read_test_source_data["test__get_and_insert_final_key_value_5"]
        schema_property = "sc1.sc2"
        components = read_test_components["test__get_and_insert_final_key_value_5"]
        final_key = "st2"
        schema_link_list = {}

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert str(e.value) == f"データ構造が定義と異なっています。({schema_property})"

    def test__add_property_1(self, read_test_new_schema, read_test_expected_schema):
        """（正常系テスト）スキーマに既にリスト構造が存在しており、そのリストがストレージと対応付いていない場合のテストケースです。"""

        new_schema = read_test_new_schema["test__add_property_1"]
        schema_property = "sc1[].sc3"
        type = "string"
        storage_data = ["value2"]
        schema_link_list = {}

        expected_schema = read_test_expected_schema["test__add_property_1"]

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_2(self, read_test_expected_schema):
        """ストレージにデータが存在しない場合のテストケースです。（正常系テスト 21)"""

        new_schema = {}
        schema_property = "sc1.sc2[]"
        type = "string"
        storage_data = []
        schema_link_list = {}

        expected_schema = read_test_expected_schema["test__add_property_2"]

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_3(self, read_test_expected_schema):
        """ストレージにデータが存在しない場合（リスト）のテストケースです。（正常系テスト 22)"""

        new_schema = {}
        schema_property = "sc1.sc2"
        type = "string"
        storage_data = []
        schema_link_list = {}

        expected_schema = read_test_expected_schema["test__add_property_3"]

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_4(self, read_test_new_schema, read_test_expected_schema):
        """（正常系テスト）既にデータが存在しているリストにデータを加える場合のテストケースです。"""

        new_schema = read_test_new_schema["test__add_property_4"]
        schema_property = "sc1.sc2[]"
        type = "string"
        storage_data = ["value3", "value4"]
        schema_link_list = {}

        expected_schema = read_test_expected_schema["test__add_property_4"]

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_5(self, read_test_new_schema):
        """（異常系テスト）既にdict構造をもつキーに対してlistとしてアクセスしようとした場合のテストケースです。"""

        new_schema = read_test_new_schema["test__add_property_5"]
        schema_property = "sc1[].sc3"
        type = "string"
        storage_data = ["value2"]
        schema_link_list = {}

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert str(e.value) == f"マッピング定義に誤りがあります。({schema_property})"

    def test__add_property_6(self, read_test_new_schema):
        """（異常系テスト）既にlist構造をもつキーに対してdictとしてアクセスしようとした場合のテストケースです。"""

        new_schema = read_test_new_schema["test__add_property_6"]
        schema_property = "sc1.sc3"
        type = "string"
        storage_data = ["value2"]
        schema_link_list = {}

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert str(e.value) == f"マッピング定義に誤りがあります。({schema_property})"

    def test__add_property_7(self, mocker):
        """（異常系テスト）無効なtypeが定義されていた場合のテストケースです。"""

        new_schema = {}
        schema_property = "sc1.sc2"
        type = "invalid_type"
        storage_data = ["value1"]
        schema_link_list = {}

        mocker.patch("dg_mm.models.grdm.GrdmMapping._convert_data_type", side_effect=MappingDefinitionError)

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert str(e.value) == f"type:{type}は有効な型ではありません。({schema_property})"

    def test__convert_data_type_1(self):
        """（正常系テスト）bool型のデータをstring型に変換する場合のテストケースです。"""
        data = [True, False]
        type = "string"

        expected_data = ["True", "False"]

        target_class = GrdmMapping()
        converted_data = target_class._convert_data_type(data, type)

        assert converted_data == expected_data

    def test__convert_data_type_2(self):
        """（正常系テスト）bool型のデータをbool型に変換する場合のテストケースです。"""
        data = [True]
        type = "boolean"

        expected_data = [True]

        target_class = GrdmMapping()
        converted_data = target_class._convert_data_type(data, type)

        assert converted_data == expected_data

    def test__convert_data_type_3(self):
        """（正常系テスト）string型のデータをbool型に変換する場合のテストケースです。"""
        data = ["True", "false", "TRUE"]
        type = "boolean"

        expected_data = [True, False, True]

        target_class = GrdmMapping()
        converted_data = target_class._convert_data_type(data, type)

        assert converted_data == expected_data

    def test__convert_data_type_4(self):
        """（正常系テスト）小数点を含む数値のstring型データをfloat型に変換する場合のテストコードです。"""
        data = ["1.156"]
        type = "number"

        expected_data = [1.156]

        target_class = GrdmMapping()
        converted_data = target_class._convert_data_type(data, type)

        assert converted_data == expected_data

    def test__convert_data_type_5(self):
        """（異常系テスト）データがbool型に変換できないint型の場合のテストケースです。"""
        data = [10]
        type = "boolean"

        with pytest.raises(DataTypeError):
            target_class = GrdmMapping()
            target_class._convert_data_type(data, type)

    def test__convert_data_type_6(self):
        """（異常系テスト）データがbool型に変換できないstring型の場合のテストケースです。"""
        data = ["Any"]
        type = "boolean"

        with pytest.raises(DataTypeError):
            target_class = GrdmMapping()
            target_class._convert_data_type(data, type)

    def test__convert_data_type_7(self):
        """（異常系テスト）スキーマのデータの型が定義されていない場合のテストケースです。"""
        data = ["text"]
        type = None

        with pytest.raises(MappingDefinitionError):
            target_class = GrdmMapping()
            target_class._convert_data_type(data, type)

    def test__add_unmap_property_1(self, read_test_expected_schema):
        """(正常系テスト)空のスキーマにプロパティを追加する場合のテストケースです。"""

        current_schema = {}
        schema_properties = ["sc1", "sc2"]

        expected_schema = read_test_expected_schema["test__add_unmap_property_1"]

        # テスト実行
        target_class = GrdmMapping()
        new_schema = target_class._add_unmap_property(current_schema, schema_properties)

        # 結果の確認
        assert new_schema == expected_schema

    def test__add_unmap_property_2(self, read_test_expected_schema):
        """(正常系テスト)空のスキーマにリストのプロパティを追加する場合のテストケースです。"""

        current_schema = {}
        schema_properties = ["sc1[]", "sc2"]

        expected_schema = read_test_expected_schema["test__add_unmap_property_2"]

        # テスト実行
        target_class = GrdmMapping()
        new_schema = target_class._add_unmap_property(current_schema, schema_properties)

        # 結果の確認
        assert new_schema == expected_schema

    def test__add_unmap_property_3(self, read_test_new_schema, read_test_expected_schema):
        """(正常系テスト)1つ上の階層まですでにスキーマに存在するプロパティを追加する場合のテストケースです。"""

        current_schema = read_test_new_schema["test__add_unmap_property_3"]
        schema_properties = ["sc1", "sc2[]", "sc3"]

        expected_schema = read_test_expected_schema["test__add_unmap_property_3"]

        # テスト実行
        target_class = GrdmMapping()
        new_schema = target_class._add_unmap_property(current_schema, schema_properties)

        # 結果の確認
        assert new_schema == expected_schema

    def test__add_unmap_property_4(self, read_test_new_schema):
        """(異常系テスト)プロパティがリストとして定義されているのにスキーマにリスト以外が存在する場合のテストケースです。"""

        current_schema = read_test_new_schema["test__add_unmap_property_4"]
        schema_properties = ["sc1", "sc2[]", "sc3"]

        # テスト実行
        with pytest.raises(MappingDefinitionError):
            target_class = GrdmMapping()
            target_class._add_unmap_property(current_schema, schema_properties)

    def test__add_unmap_property_5(self, read_test_new_schema):
        """(異常系テスト)プロパティがオブジェクトとして定義されているのにスキーマにオブジェクト以外が存在する場合のテストケースです。"""

        current_schema = read_test_new_schema["test__add_unmap_property_5"]
        schema_properties = ["sc1", "sc2", "sc3"]

        # テスト実行
        with pytest.raises(MappingDefinitionError):
            target_class = GrdmMapping()
            target_class._add_unmap_property(current_schema, schema_properties)

    def test__add_unmap_property_6(self, read_test_new_schema):
        """(異常系テスト)一番下の階層なのにすでにスキーマにプロパティが存在する場合のテストケースです。"""

        current_schema = read_test_new_schema["test__add_unmap_property_6"]
        schema_properties = ["sc1", "sc2"]

        # テスト実行
        with pytest.raises(MappingDefinitionError):
            target_class = GrdmMapping()
            target_class._add_unmap_property(current_schema, schema_properties)


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

        with pytest.raises(InvalidTokenError, match="認証に失敗しました。"):
            target_class._check_token_valid()

    def test__check_token_valid_failure_2(self, mocker):
        """トークンのアクセス権がない"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_profile_2.json')
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(AccessDeniedError, match="トークンのアクセス権が不足しています。"):
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

    def test__check_token_valid_failure_5(self, mocker):
        """予期せぬエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(429))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "invalid_token"

        with pytest.raises(requests.HTTPError):
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

        with pytest.raises(InvalidIdError, match="プロジェクトが存在しません。"):
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

    def test__check_project_id_valid_failure_4(self, mocker):
        """プロジェクトが削除されている"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(410))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "invalid_project_id"

        with pytest.raises(InvalidIdError, match="プロジェクトが削除されています"):
            target_class._check_project_id_valid()

    def test__check_project_id_valid_failure_5(self, mocker):
        """APIエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(500))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "invalid_project_id"

        with pytest.raises(APIError, match="APIサーバーでエラーが発生しました"):
            target_class._check_project_id_valid()

    def test__check_project_id_valid_failure_6(self, mocker):
        """APIエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(429))

        # テスト実行
        target_class = GrdmAccess()
        target_class._token = "valid_token"
        target_class._project_id = "invalid_project_id"

        with pytest.raises(requests.HTTPError):
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
        with pytest.raises(MetadataNotFoundError, match="指定したIDのプロジェクトメタデータが存在しません。"):
            instance.get_project_metadata(project_metadata_id="invalid")

    def test_get_project_metadata_failure_2(self, mocker):
        """別のプロジェクトが持つプロジェクトメタデータIDを指定"""

        # モック化
        api_res = read_json('tests/models/data/grdm_api_registrations_4.json')  # 別のプロジェクトのメタデータIDを指定した場合のレスポンス
        mocker.patch('requests.get', return_value=create_mock_response(200, api_res))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(MetadataNotFoundError, match="指定したIDのプロジェクトメタデータが存在しません。"):
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

    def test_get_project_metadata_failure_6(self, mocker):
        """予期せぬエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(429))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(requests.HTTPError):
            instance.get_project_metadata()

    def test_get_file_metadata_success_1(self, mocker):
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

    def test_get_file_metadata_success_2(self, mocker):
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

    def test_get_file_metadata_success_3(self, mocker):
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

    def test_get_file_metadata_success_4(self, mocker):
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

    def test_get_file_metadata_failure_4(self, mocker):
        """予期せぬエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(429))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(requests.HTTPError):
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

    def test_get_project_info_failure_4(self, mocker):
        """予期せぬエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(429))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(requests.HTTPError):
            instance.get_project_info()

    def test_get_member_info_success_1(self, mocker):
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

    def test_get_member_info_success_2(self, mocker):
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

    def test_get_member_info_success_3(self, mocker):
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

    def test_get_member_info_failure_4(self, mocker):
        """予期せぬエラーが発生する"""

        # モック化
        mocker.patch('requests.get', return_value=create_mock_response(429))

        # テスト実行
        instance = create_authorized_grdm_access()
        with pytest.raises(requests.HTTPError):
            instance.get_member_info()

    def test_get_member_info_failure_5(self, mocker):
        """無限ループ回避処理の確認"""

        # モック化
        api_res1 = read_json('tests/models/data/grdm_api_contributors_3.json')  # メンバー情報が11件登録されている場合の1回目のレスポンス
        mock_obj = mocker.patch('requests.get', return_value=create_mock_response(200, api_res1))

        # テスト実行
        instance = create_authorized_grdm_access()
        max_requests = instance._max_requests
        with pytest.raises(APIError, match="リクエスト回数が上限を超えました"):
            instance.get_member_info()

        # 結果の確認
        assert mock_obj.call_count == max_requests
