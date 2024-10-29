"""grdm.pyをテストするためのモジュールです。"""
import json
from multiprocessing import AuthenticationError
from typing import Counter

import pytest

from dg_mm.errors import (
    DataFormatError,
    MappingDefinitionError,
    MetadataTypeError,
    NotFoundKeyError
)
from dg_mm.models.grdm import GrdmAccess, GrdmMapping


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


class TestGrdmMapping():
    """GrdmMappingクラスをテストするためのクラスです。"""

    def test_mapping_metadata_1(self, mocker):
        """(正常系テスト 4)スキーマ全体のメタデータを取得する場合のテストケースです。"""
        #テスト用の仮のマッピング定義
        test_mapping_definition = {
            "sc1[].sc2[]": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3",
                "list": {
                    "st1": "sc1"
                }
            },
            "sc1[].sc3[].sc4[]": {
                "type": "string",
                "value": None
            },
            "sc1[].sc3[].sc5": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3.st4",
                "list": {
                    "st1": "sc1",
                    "st3": "sc3"
                }
            }
        }
        metadata_sources = ["member_info"]
        source_data = {}
        #テスト用のマッピング定義から期待されるスキーマ
        expected_new_schema = {
            "sc1": [
                {
                    "sc2": ["value1"],
                    "sc3": [
                        {
                            "sc4": [],
                            "sc5": "value2"
                        }
                    ]
                }
            ]
        }
        #_mapping_metadata内で呼び出す各関数をモック化
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__add_property = mocker.patch("dg_mm.models.grdm.GrdmMapping._add_property", return_value=expected_new_schema)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", return_value=expected_new_schema)

        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata("リサーチフロー", "valid_token", "valid_project_id",)
        #戻り値が期待通りかの検証
        assert metadata == expected_new_schema
        #モック化した各関数が想定された数だけ呼び出されているかの検証
        assert mock__add_property.call_count == 1
        assert mock__extract_and_insert_metadata.call_count == 2
        #各プロパティが正確に処理されているかの検証
        schema_property_arg = mock__add_property.call_args_list[0][0][1]
        assert schema_property_arg == "sc1[].sc3[].sc4[]"

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[0][0][2]
        assert schema_property_arg == "sc1[].sc2[]"

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[1][0][2]
        assert schema_property_arg == "sc1[].sc3[].sc5"

    def test_mapping_metadata_2(self, mocker):
        """(正常系テスト 5)filter_propertiesで指定されたプロパティのメタデータのみを取得する場合のテストケースです。"""

        filter_properties = ["sc1.sc2", "sc1.sc3.sc5"]
        test_mapping_definition = {
            "sc1[].sc2[]": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3",
                "list": {
                    "st1": "sc1"
                }
            },
            "sc1[].sc3[].sc5": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3.st4",
                "list": {
                    "st1": "sc1",
                    "st3": "sc3"
                }
            }
        }
        metadata_sources = ["project_info", "member_info"]
        source_data = {}
        expected_new_schema = {
            "sc1": [
                {
                    "sc2": ["value1"],
                    "sc3": [
                        {
                            "sc5": "value2"
                        }
                    ]
                }
            ]
        }
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mock_get_project_info = mocker.patch("dg_mm.models.grdm.GrdmAccess.get_project_info", return_value=source_data)
        mock_get_member_info = mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", return_value=expected_new_schema)

        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata(
            "リサーチフロー", "valid_token", "valid_project_id", filter_properties)

        assert metadata == expected_new_schema

        assert mock_get_project_info.call_count == 1
        assert mock_get_member_info.call_count == 1
        assert mock__extract_and_insert_metadata.call_count == 2

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[0][0][2]
        assert schema_property_arg == "sc1[].sc2[]"

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[1][0][2]
        assert schema_property_arg == "sc1[].sc3[].sc5"

    def test_mapping_metadata_3(self, mocker):
        """(正常系テスト 6)filter_propertiesで指定されたすべてのプロパティに対応するメタデータが存在しない場合のテストケースです。"""

        filter_properties = ["sc1.sc2", "sc1.sc3.sc4[]"]
        test_mapping_definition = {
            "sc1[].sc2": {
                "type": "string",
                "value": None
            },
            "sc1[].sc3[].sc4[]": {
                "type": "string",
                "value": None,
            }
        }
        metadata_sources = []
        expected_new_schema = {
            "sc1": [
                {
                    "sc2" : None,
                    "sc3": [
                        {
                            "sc4": []
                        }
                    ]
                }
            ]
        }
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mock__add_property = mocker.patch("dg_mm.models.grdm.GrdmMapping._add_property", return_value=expected_new_schema)

        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata(
            "リサーチフロー", "valid_token", "valid_project_id", filter_properties)

        assert metadata == expected_new_schema

        assert mock__add_property.call_count == 2

        schema_property_arg = mock__add_property.call_args_list[0][0][1]
        assert schema_property_arg == "sc1[].sc2"

        schema_property_arg = mock__add_property.call_args_list[1][0][1]
        assert schema_property_arg == "sc1[].sc3[].sc4[]"

    def test_mapping_metadata_4(self, mocker):
        """(異常系テスト 7)GRDMの認証に失敗した場合のテストケースです。"""

        #認証を行う関数が呼ばれた際にエラーを返すようにモック化
        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication", side_effect=AuthenticationError("認証に失敗しました。"))

        #AuthenticationErrorをキャッチする形でテストを実行
        with pytest.raises(AuthenticationError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id")

        assert str(e.value) == "認証に失敗しました。"

    def test_mapping_metadata_5(self, mocker):
        """(異常系テスト 8)マッピング定義ファイルの読み込みに失敗した場合のテストケースです。"""

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=MappingDefinitionError("マッピング定義ファイルの読み込みに失敗しました。"))

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id")

        assert str(e.value) == "マッピング定義ファイルの読み込みに失敗しました。"

    def test_mapping_metadata_6(self, mocker):
        """(異常系テスト 9)filter_properties(取得するプロパティ一覧)が空の場合のテストケースです。"""

        filter_properties = []

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=NotFoundKeyError("絞り込むプロパティが指定されていません。"))

        with pytest.raises(NotFoundKeyError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id", filter_properties)

        assert str(e.value) == "絞り込むプロパティが指定されていません。"

    def test_mapping_metadata_7(self, mocker):
        """(異常系テスト 10)filter_propertiesとして存在しないプロパティが指定された場合のテストケースです。"""

        filter_properties = ["non_existent_property"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=NotFoundKeyError("指定したプロパティが存在しません。"))

        with pytest.raises(NotFoundKeyError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("リサーチフロー", "invalid_token", "invalid_project_id", filter_properties)

        assert str(e.value) == "指定したプロパティが存在しません。"

    def test_mapping_metadata_8(self, mocker):
        """(異常系テスト 11),metadata_sourcesに存在する取得先からのメタデータの取得に失敗した場合のテストケースです。"""

        metadata_sources = ["project_info", "member_info", "project_metadata", "file_metadata"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition")
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_project_info", side_effect=Exception("メタデータの取得に失敗しました。"))

        with pytest.raises(Exception) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("リサーチフロー", "invalid_token", "invalid_project_id")

        assert str(e.value) == "メタデータの取得に失敗しました。"

    def test_mapping_metadata_9(self, mocker):
        """(異常系テスト 12),マッピングに失敗した場合のエラーケースです。"""

        test_mapping_definition = {
            "sc1[].sc2[]": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3",
                "list": {
                    "st1": "sc1"
                }
            },
            "sc1[].sc3[].sc4[]": {
                "type": "string",
                "value": None
            },
            "sc1[].sc3[].sc5": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3.st4",
                "list": {
                    "st1": "sc1",
                    "st3": "sc3"
                }
            }
        }
        metadata_sources = ["member_info"]
        source_data = {}

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=MappingDefinitionError("マッピングに失敗しました。"))

        with pytest.raises(MappingDefinitionError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("リサーチフロー", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 1
        assert str(e.value) == "マッピングに失敗しました。"

    def test_mapping_metadata_10(self, mocker):
        """(異常系テスト)_find_metadata_sourcesで特定した取得先の中にGRDMに存在しない取得先が含まれていた場合のテストケースです。"""
        test_mapping_definition ={}
        metadata_sources =["project_info", "non_existent_info", "file_metadata", "non_existent_metadata" ]
        error_sources = ["non_existent_info", "non_existent_metadata"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mock_get_project_info =mocker.patch("dg_mm.models.grdm.GrdmAccess.get_project_info")
        mock_get_file_matadata = mocker.patch("dg_mm.models.grdm.GrdmAccess.get_file_metadata")

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("リサーチフロー", "valid_token", "valid_project_id")

        assert mock_get_project_info.call_count == 1
        assert mock_get_file_matadata.call_count == 1
        assert str(e.value) == f"メタデータ取得先:{error_sources}が存在しません"

    def test_mapping_metadata_11(self, mocker):
        """(異常系テスト)一致するストレージのキーが存在しない場合のテストケースです。"""
        test_mapping_definition = {
            "sc1[].sc2[]": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3",
                "list": {
                    "st1": "sc1"
                }
            },
            "sc1[].sc3": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st3",
                "list": {
                    "st1": "sc1"
                }
            }
        }
        metadata_sources = ["member_info"]
        source_data = {}
        error_keys = ["sc1と一致するストレージのキーが見つかりませんでした。(sc1[].sc2[])"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect = [NotFoundKeyError(error_keys), NotFoundKeyError("sc3と一致するストレージのキーが見つかりませんでした。(sc1[].sc3)")])

        with pytest.raises(NotFoundKeyError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("リサーチフロー", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 2
        assert str(e.value) == "キーの不一致が確認されました。:['sc1と一致するストレージのキーが見つかりませんでした。(sc1[].sc2[])', 'sc3と一致するストレージのキーが見つかりませんでした。(sc1[].sc3)']"

    def test_mapping_metadata_12(self, mocker):
        """(異常系テスト)データの型変換に失敗した場合のテストケースです。"""
        test_mapping_definition = {
            "sc1[].sc2[]": {
                "type": "boolean",
                "source": "member_info",
                "value": "st1.st2.st3",
                "list": {
                    "st1": "sc1"
                }
            },
            "sc1[].sc3": {
                "type": "number",
                "source": "member_info",
                "value": "st1.st3",
                "list": {
                    "st1": "sc1"
                }
            }
        }
        metadata_sources = ["member_info"]
        source_data = {}

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=[MetadataTypeError("型変換エラー：storage_dataをbooleanに変換できません(sc1[].sc2[])"), MetadataTypeError("型変換エラー：storage_dataをnumberに変換できません(sc1[].sc3)")])

        with pytest.raises(MetadataTypeError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("リサーチフロー", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 2
        assert str(e.value) == "データの変換に失敗しました。：['型変換エラー：storage_dataをbooleanに変換できません(sc1[].sc2[])', '型変換エラー：storage_dataをnumberに変換できません(sc1[].sc3)']"

    def test_mapping_metadata_13(self, mocker):
        """(異常系テスト)ストレージのキーが一致しないエラーとデータの型変換に失敗したエラーの両方が発生した場合のテストケースです。"""
        test_mapping_definition = {
            "sc1[].sc2[]": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3",
                "list": {
                    "st1": "sc1"
                }
            },
            "sc1[].sc3": {
                "type": "number",
                "source": "member_info",
                "value": "st1.st3",
                "list": {
                    "st1": "sc1"
                }
            }
        }
        metadata_sources = ["member_info"]
        source_data = {}
        error_keys = ["sc1と一致するストレージのキーが見つかりませんでした。(sc1[].sc2[])"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=test_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=source_data)
        mock__extract_and_insert_metadata = mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=[NotFoundKeyError(error_keys), MetadataTypeError(f"型変換エラー：storage_dataをnumberに変換できません(sc1[].sc3)")])

        with pytest.raises(DataFormatError)as e:
            target_class = GrdmMapping()
            target_class.mapping_metadata("リサーチフロー", "valid_token", "valid_project_id")

        assert mock__extract_and_insert_metadata.call_count == 2
        assert str(e.value) ==  "キーの不一致が確認されました。:['sc1と一致するストレージのキーが見つかりませんでした。(sc1[].sc2[])'], データの変換に失敗しました。：['型変換エラー：storage_dataをnumberに変換できません(sc1[].sc3)']"

    def test__find_metadata_sources_1(self):
        """(正常系テスト 7)マッピング定義にある全取得先を取得する場合のテストケースです。"""
        test_mapping_definition = {
            "sc1[].sc2[]": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3",
                "list": {
                    "st1": "sc1"
                }
            },
            "sc1[].sc3[].sc4[]": {
                "type": "string",
                "source" : "project_info",
                "value": "st1.st6"
            },
            "sc1[].sc3[].sc5": {
                "type": "string",
                "source": "member_info",
                "value": "st1.st2.st3.st4",
                "list": {
                    "st1": "sc1",
                    "st3": "sc3"
                }
            }
        }
        expected_metadata_sources = ["project_info", "member_info"]

        target_class = GrdmMapping()
        #インスタンス変数にテスト用のマッピング定義を設定
        target_class._mapping_definition = test_mapping_definition

        metadata_sources = target_class._find_metadata_sources()

        assert Counter(metadata_sources) == Counter(expected_metadata_sources)

    def test__find_metadata_sources_2(self):
        """(正常系テスト 8)マッピング定義に取得先が一つも存在しない場合のテストケースです。"""
        test_mapping_definition = {
            "researcher[].email[]": {
                "type": "string",
                "value": None,
            },
            "researcher[].affiliation[].adress[]": {
                "type": "string",
                "value": None
            },
            "researcher[].affiliation[].name": {
                "type": "string",
                "value": None,
            }
        }

        target_class = GrdmMapping()
        target_class._mapping_definition = test_mapping_definition
        metadata_sources = target_class._find_metadata_sources()

        assert not metadata_sources

    def test__extract_and_insert_metadata_1(self):
        """(正常系テスト 9)マッピングのテストケースNo.1のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": "value1"
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": "value1"
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_2(self):
        """(正常系テスト 10)マッピングのテストケースNo.2のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2[]"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": [
                        "value1",
                        "value2"
                    ]
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": ["value1",
                        "value2"
                        ]
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_3(self):
        """(正常系テスト 11)マッピングのテストケースNo.3のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2"
        components = {
            "type": "number",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": "1"
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": 1
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_4(self):
        """(正常系テスト 12)マッピングのテストケースNo.4のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2[]"
        components = {
            "type": "number",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": [
                        "1",
                        "2"
                    ]
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": [
                    1,
                    2
                ]
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_5(self):
        """(正常系テスト 13)マッピングのテストケースNo.5のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2[]"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": "value1"
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": [
                    "value1"
                ]
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_6(self):
        """(正常系テスト 14)マッピングのテストケースNo.6のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2[]"
        components = {
            "type": "number",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": "1"
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": [
                    1
                ]
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_7(self):
        """(正常系テスト 15)マッピングのテストケースNo.7のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": [
                        "value1",
                        "value2"
                    ]
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": "value1"
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_8(self):
        """(正常系テスト 16)マッピングのテストケースNo.8のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2"
        components = {
            "type": "number",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": [
                        "1",
                        "2"
                    ]
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": 1
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_9(self):
        """(正常系テスト 17)マッピングのテストケースNo.9のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1[].sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3",
            "list": {
                "st1.st2": "sc1"
            }
        }
        sources = {
            "st1": {
                "st2": [
                    {
                        "st3": "value1"
                    },
                    {
                        "st3": "value2"
                    }
                ]
            }
        }
        excepted_schema = {
            "sc1": [
                {
                    "sc2": "value1"
                },
                {
                    "sc2": "value2"
                }
            ]
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_10(self):
        """(正常系テスト 18)マッピングのテストケースNo.10のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1[].sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": "value1"
                }
            }
        }
        excepted_schema = {
            "sc1": [
                {
                    "sc2": "value1"
                }
            ]
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_11(self):
        """(正常系テスト 19)マッピングのテストケースNo.11のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3",
            "list": {
                "st1.st2": 0
            }
        }
        sources = {
            "st1": {
                "st2": [
                    {
                        "st3": "value1"
                    },
                    {
                        "st3": "value2"
                    }
                ]
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": "value1"
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_12(self):
        """(正常系テスト 20)マッピングのテストケースNo.12のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3", "st4"]
        schema_property = "sc1[].sc2.sc3[].sc4"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3.st4",
            "list": {
                "st1": "sc1",
                "st1.st2": 0
            }
        }
        sources = {
            "st1": [
                {
                    "st2": [
                        {
                            "st3": {
                                "st4": "value1"
                            }
                        },
                        {
                            "st3": {
                                "st4": "value2"
                            }
                        }
                    ]
                },
                {
                    "st2": [
                        {
                            "st3": {
                                "st4": "value3"
                            }
                        }
                    ]
                }
            ]
        }
        excepted_schema = {
            "sc1": [
                {
                    "sc2": {
                        "sc3": [
                            {
                                "sc4": "value1"
                            }
                        ]
                    }
                },
                {
                    "sc2": {
                        "sc3": [
                            {
                                "sc4": "value3"
                            }
                        ]
                    }
                }
            ]
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_13(self):
        """(正常系テスト 23)マッピングのテストケースNo.15のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3",
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": None
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": None
            }
        }
        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_14(self):
        """(正常系テスト 24)マッピングのテストケースNo.16のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2[]"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": []
                }
            }
        }
        excepted_schema = {
            "sc1": {
                "sc2": []
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_15(self):
        """(異常系テスト 15)マッピングのテストケースNo.17のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2[]"
        components = {
            "type": "number",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": "value1"
                }
            }
        }

        target_class = GrdmMapping()
        with pytest.raises(MetadataTypeError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"型変換エラー：['value1']をnumberに変換できません({schema_property})"

    def test__extract_and_insert_metadata_16(self):
        """(異常系テスト 16)マッピングのテストケースNo.18のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2[]"
        components = {
            "type": "number",
            "source": "project_metadata",
            "value": "st1.st2.st3"
        }
        sources = {
            "st1": {
                "st2": {
                    "st3": [
                        "value1",
                        "value2"
                    ]
                }
            }
        }

        target_class = GrdmMapping()
        with pytest.raises(MetadataTypeError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"型変換エラー：['value1', 'value2']をnumberに変換できません({schema_property})"

    def test__extract_and_insert_metadata_17(self):
        """(異常系テスト 17)マッピングのテストケースNo.19のテストです。"""
        new_schema = {
            "sc1": [
                {
                    "sc2": "value1"
                }
            ]
        }
        schema_link_list = {}
        storage_keys = ["st1", "st3"]
        schema_property = "sc1.sc3"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st3"
        }
        sources = {
            "st1": [
                {
                    "st2": "value1",
                    "st3": "value2"
                }
            ]
        }

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"リスト：st1の定義が不足しています。({schema_property})"

    def test__extract_and_insert_metadata_18(self):
        """(異常系テスト 18)マッピングのテストケースNo.20のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2"
        }
        sources = {
            "st1": [
                {
                    "st2": "value1"
                }
            ]
        }

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"リスト：st1の定義が不足しています。({schema_property})"

    def test__extract_and_insert_metadata_19(self):
        """(異常系テスト 19)マッピングのテストケースNo.21のテストです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
        schema_property = "sc1[].sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
            "list": {
                "st1": "sc1"
            }
        }
        sources = {
            "st1": {
                "st2": "value1"
            }
        }

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"オブジェクト：st1がリストとして定義されています。({schema_property})"

    def test__extract_and_insert_metadata_20(self):
        """(異常系テスト 20)マッピングのテストケースNo.22のテストです。"""
        new_schema = {
            "sc1": [
                {
                    "sc2": {
                        "sc3": [
                            {
                                "sc4": "value1"
                            },
                            {
                                "sc4": "value3"
                            }
                        ]
                    }
                },
                {
                    "sc2": {
                        "sc3": [
                            {
                                "sc4": "value5"
                            }
                        ]
                    }
                }
            ]
        }
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3", "st5"]
        schema_property = "sc1[].sc2.sc3[].sc5"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3.st5",
            "list": {
                "st1": "sc1",
                "st1.st2": 0
            }
        }
        sources = {
            "st1": [
                {
                    "st2": [
                        {
                            "st3": {
                                "st4": "value1",
                                "st5": "value2"
                            }
                        },
                        {
                            "st3": {
                                "st4": "value3",
                                "st5": "value4"
                            }
                        }
                    ]
                },
                {
                    "st2": [
                        {
                            "st3": {
                                "st4": "value5",
                                "st5": "value6"
                            }
                        }
                    ]
                }
            ]
        }

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._extract_and_insert_metadata(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert str(e.value) == f"マッピング定義に誤りがあります({schema_property})"

    def test__check_and_handle_key_structure_1(self):
        """（異常系テスト）ストレージに一致するキーが存在しなかった場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st0", "st2"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st0.st2"
        }
        sources = {
            "st1": {
                "st2": "value1"
            }
        }
        index = 0
        key = "st0"

        target_class = GrdmMapping()
        with pytest.raises(NotFoundKeyError) as e:
            new_schema = target_class._check_and_handle_key_structure(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert str(e.value) == f"st0と一致するストレージのキーが見つかりませんでした。({schema_property})"

    def test__check_and_handle_key_structure_2(self):
        """（異常系テスト）ストレージにキーが不足していた場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
        }
        sources = {
            "st1": "value1"
        }
        index = 0
        key = "st1"

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            new_schema = target_class._check_and_handle_key_structure(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert str(e.value) == f"データ構造が定義と異なっています。({schema_property})"

    def test__handle_list_1(self):
        """（異常系テスト）リスト内のオブジェクトに期待されるキーが存在しないものが含まれる場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1[].sc2.sc3"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3",
            "list" : {
                "st1" : "sc1"
            }
        }
        sources = {
            "st1": [
                {
                    "st4": "value1"
                },
                {
                    "st2": {
                        "st3" :"value2"
                    },
                    "st3": "value3"
                },
                {
                    "st3": "value4"
                }
            ]
        }
        index = 0
        key = "st1"

        target_class = GrdmMapping()
        with pytest.raises(NotFoundKeyError) as e:
            target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert e.value.args[0] == [f"st2と一致するストレージのキーが見つかりませんでした。({schema_property})",
                                    f"st2と一致するストレージのキーが見つかりませんでした。({schema_property})"]

    def test__handle_list_2(self):
        """（異常系テスト）異なる複数のリスト内にキーが存在しないオブジェクトが存在する場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3", "st4"]
        schema_property = "sc1[].sc2[].sc3"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3.st4",
            "list": {
                "st1": "sc1",
                "st1.st2": "sc1.sc2"
            }
        }
        sources = {
            "st1": [
                {
                    "st4": "value1"
                },
                {
                    "st2": [
                        {
                            "st3": {
                                "st4": "value2"                                }
                        },
                    ]
                },
                {
                    "st2": [
                        {
                            "st4": "value3"
                        },
                    ]
                },                ]
        }
        index = 0
        key = "st1"

        with pytest.raises(NotFoundKeyError) as e:
            target_class = GrdmMapping()
            target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert e.value.args[0] == [f"st2と一致するストレージのキーが見つかりませんでした。({schema_property})",
                                    f"['st3と一致するストレージのキーが見つかりませんでした。({schema_property})']"]

    def test__handle_list_3(self):
        """（異常系テスト）マッピング定義の'list'で指定されたインデックスに対応するデータがストレージに存在しない場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
            "list" : {
                "st1" : 2
            }
        }
        sources = {
            "st1": [
                {
                    "st2": "value1"
                }
            ]
        }
        index = 0
        key = "st1"

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert str(e.value) ==  f"指定されたインデックス:2が存在しません({schema_property})"

    def test__get_and_insert_final_key_value_1(self):
        """（正常系テスト）末端のキーが存在しない場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
        }
        source = {}
        final_key = "st2"

        excepted_schema ={
            "sc1" : {
                "sc2" :None
            }
        }

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert new_schema == excepted_schema

    def test__get_and_insert_final_key_value_2(self):
        """（正常系テスト）末端のキーがリストであり、その値と対応するリストが存在する場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        schema_property = "sc1[].sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
            "list" : {
                "st1.st2" :"sc1"
            }
        }
        source = {
            "st2": [
                "value1",
                "value2"
            ]
        }
        final_key = "st2"
        expected_schema ={
            "sc1" :[
                {
                    "sc2" :"value1"
                },
                {
                    "sc2" : "value2"
                }
            ]
        }

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert new_schema == expected_schema

    def test__get_and_insert_final_key_value_3(self):
        """（正常系テスト）末端のキーがリストであり、その値と対応するリストが存在しない場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
            "list" : {
                "st1.st2" : 1
            }
        }
        source = {
            "st2": [
                "value1",
                "value2"
            ]
        }
        final_key = "st2"
        expected_schema ={
            "sc1" :{
                    "sc2" :"value2"
                }
        }

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert new_schema == expected_schema

    def test__get_and_insert_final_key_value_4(self):
        """（異常系テスト）'list'に記載された末端のキーのリストのインデックスと対応するデータが存在しない場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
            "list" : {
                "st1.st2" : 3
            }
        }
        source = {
            "st2": [
                "value1",
                "value2"
            ]
        }
        final_key = "st2"

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert str(e.value) == f"指定されたインデックスが存在しません({schema_property})"

    def test__get_and_insert_final_key_value_5(self ):
        """（異常系テスト）マッピング定義に記載されているストレージのキーが不足している場合のテストケースです。"""
        new_schema = {}
        schema_link_list = {}
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
        }
        source = {
            "st2": {
                "st3" :"value1"
            }
        }
        final_key = "st2"

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, final_key, schema_link_list)

        assert str(e.value) == f"データ構造が定義と異なっています({schema_property})"

    def test__add_property_1(self):
        """（正常系テスト）スキーマに既にリスト構造が存在しており、そのリストがストレージと対応付いていない場合のテストケースです。"""
        new_schema = {
            "sc1" :[
                {
                    "sc2" : "value1"
                }
            ]
        }
        schema_property = "sc1[].sc3"
        type = "string"
        storage_data = ["value2"]
        schema_link_list = {}

        expected_schema = {
            "sc1" :[
                {
                    "sc2" : "value1",
                    "sc3" : "value2"
                }
            ]
        }

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_2(self):
        """ストレージにデータが存在しない場合のテストケースです。（正常系テスト 21)"""
        new_schema = {}
        schema_property = "sc1.sc2[]"
        type = "string"
        storage_data = []
        schema_link_list = {}

        expected_schema = {
            "sc1" :{
                "sc2" : []
                }
        }

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_3(self):
        """ストレージにデータが存在しない場合（リスト）のテストケースです。（正常系テスト 22)"""
        new_schema = {}
        schema_property = "sc1.sc2"
        type = "string"
        storage_data = []
        schema_link_list = {}

        expected_schema = {
            "sc1" :{
                "sc2" : None
                }
        }

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_4(self):
        """（正常系テスト）既にデータが存在しているリストにデータを加える場合のテストケースです。"""
        new_schema = {
            "sc1" : {
                    "sc2" : [
                        "value1",
                        "value2"
                    ]
                }
        }
        schema_property = "sc1.sc2[]"
        type = "string"
        storage_data = ["value3", "value4"]
        schema_link_list = {}

        expected_schema = {
            "sc1" :{
                    "sc2" : [
                        "value1",
                        "value2",
                        "value3",
                        "value4"
                    ]
                }
        }

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert new_schema == expected_schema

    def test__add_property_5(self):
        """（異常系テスト）既にdict構造をもつキーに対してlistとしてアクセスしようとした場合のテストケースです。"""
        new_schema = {
            "sc1": {
                "sc2": "value1"
            }
        }
        schema_property = "sc1[].sc3"
        type = "string"
        storage_data = ["value2"]
        schema_link_list = {}

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert str(e.value) == f"マッピング定義に誤りがあります({schema_property})"

    def test__add_property6(self):
        """（異常系テスト）既にlist構造をもつキーに対してdictとしてアクセスしようとした場合のテストケースです。"""
        new_schema = {
            "sc1": [
                {
                    "sc2": "value1"
                }
            ]
        }
        schema_property = "sc1.sc3"
        type = "string"
        storage_data = ["value2"]
        schema_link_list = {}

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert str(e.value) == f"マッピング定義に誤りがあります({schema_property})"

    def test__add_property_7(self, mocker):
        """（異常系テスト）無効なtypeが定義されていた場合のテストケースです。"""
        new_schema = {}
        schema_property = "sc1.sc2"
        type = "invalid_type"
        storage_data = ["value1"]
        schema_link_list = {}

        mocker.patch("dg_mm.models.grdm.GrdmMapping._convert_data_type", side_effect = MappingDefinitionError)

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert str(e.value) == f"type:{type}は有効な型ではありません({schema_property})"

    def test__convert_data_type_1(self):
        """（正常系テスト）bool型のデータをstring型に変換する場合のテストケースです。"""
        data =[True, False]
        type = "string"

        excepted_data = ["True", "False"]

        target_class = GrdmMapping()
        converted_data =target_class._convert_data_type(data, type)

        assert converted_data == excepted_data

    def test__convert_data_type_2(self):
        """（正常系テスト）bool型のデータをbool型に変換する場合のテストケースです。"""
        data =[True]
        type = "boolean"

        excepted_data = [True]

        target_class = GrdmMapping()
        converted_data =target_class._convert_data_type(data, type)

        assert converted_data == excepted_data

    def test__convert_data_type_3(self):
        """（正常系テスト）string型のデータをbool型に変換する場合のテストケースです。"""
        data =["True", "false", "TRUE"]
        type = "boolean"

        excepted_data = [True, False, True]

        target_class = GrdmMapping()
        converted_data =target_class._convert_data_type(data, type)

        assert converted_data == excepted_data

    def test__convert_data_type_4(self):
        """（正常系テスト）小数点を含む数値のstring型データをfloat型に変換する場合のテストコードです。"""
        data =["1.156"]
        type = "number"

        excepted_data = [1.156]

        target_class = GrdmMapping()
        converted_data =target_class._convert_data_type(data, type)

        assert converted_data == excepted_data

    def test__convert_data_type_5(self):
        """（異常系テスト）データがbool型に変換できないint型の場合のテストケースです。"""
        data =[10]
        type = "boolean"

        with pytest.raises(MetadataTypeError):
            target_class = GrdmMapping()
            target_class._convert_data_type(data, type)

    def test__convert_data_type_6(self):
        """（異常系テスト）データがbool型に変換できないstring型の場合のテストケースです。"""
        data =["Any"]
        type = "boolean"

        with pytest.raises(MetadataTypeError):
            target_class = GrdmMapping()
            target_class._convert_data_type(data, type)

    def test__convert_data_type_7(self):
        """（異常系テスト）スキーマのデータの型が定義されていない場合のテストケースです。"""
        data =["text"]
        type = None

        with pytest.raises(MappingDefinitionError):
            target_class = GrdmMapping()
            target_class._convert_data_type(data, type)
