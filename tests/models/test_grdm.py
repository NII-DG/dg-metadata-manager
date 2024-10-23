import json
from multiprocessing import AuthenticationError
from typing import Counter

import pytest

from dg_mm.exceptions import MappingDefinitionError, MetadataTypeError, NotFoundKeyError
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

    def test_mapping_metadata_1(self, mocker):

        mock_mapping_definition = {
            "researcher[].email[]": {
                "type": "string",
                "source": "member_info",
                "value": "data.embeds.users.data.attributes.email",
                "list": {
                    "data": "researcher"
                }
            },
            "researcher[].affiliation[].adress[]": {
                "type": "string",
                "value": None
            },
            "researcher[].affiliation[].name": {
                "type": "string",
                "source": "member_info",
                "value": "data.embeds.users.data.attributes.employment.institution_ja",
                "list": {
                    "data": "researcher",
                    "employment": "affiliation"
                }
            }
        }
        mock_metadata_sources = ["member_info"]
        mock_source_data = {}
        mock_new_schema = {
            "researcher": [
                {
                    "email": ["test_email"],
                    "affiliation": [
                        {
                            "adress": [],
                            "name": "test_name"
                        }
                    ]
                }
            ]
        }

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=mock_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=mock_metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=mock_source_data)
        mock__add_property = mocker.patch(
            "dg_mm.models.grdm.GrdmMapping._add_property", return_value=mock_new_schema)
        mock__extract_and_insert_metadata = mocker.patch(
            "dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", return_value=mock_new_schema)

        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata(
            "リサーチフロー", "valid_token", "valid_project_id",)

        assert isinstance(metadata, dict)
        assert metadata == mock_new_schema

        assert mock__add_property.call_count == 1
        assert mock__extract_and_insert_metadata.call_count == 2

        schema_property_arg = mock__add_property.call_args_list[0][0][1]
        assert schema_property_arg == "researcher[].affiliation[].adress[]"

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[0][0][2]
        assert schema_property_arg == "researcher[].email[]"

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[1][0][2]
        assert schema_property_arg == "researcher[].affiliation[].name"

    def test_mapping_metadata_2(self, mocker):

        filter_property = ["researcher.email", "researcher.affiliation.name"]
        mock_mapping_definition = {
            "researcher[].email[]": {
                "type": "string",
                "source": "project_info",
                "value": "data.embeds.users.data.attributes.email",
                "list": {
                    "data": "researcher"
                }
            },
            "researcher[].affiliation[].name": {
                "type": "string",
                "source": "member_info",
                "value": "data.embeds.users.data.attributes.employment.institution_ja",
                "list": {
                    "data": "researcher",
                    "employment": "affiliation"
                }
            }
        }
        mock_metadata_sources = ["project_info", "member_info"]
        mock_source_data = {}
        mock_new_schema = {
            "researcher": [
                {
                    "email": ["test_email"],
                    "affiliation": [
                        {
                            "name": "test_name"
                        }
                    ]
                }
            ]
        }

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=mock_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=mock_metadata_sources)
        mock_get_project_info = mocker.patch(
            "dg_mm.models.grdm.GrdmAccess.get_project_info", return_value=mock_source_data)
        mock_get_member_info = mocker.patch(
            "dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=mock_source_data)
        mock__extract_and_insert_metadata = mocker.patch(
            "dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", return_value=mock_new_schema)

        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata(
            "リサーチフロー", "valid_token", "valid_project_id", filter_property)

        assert isinstance(metadata, dict)
        assert metadata == mock_new_schema

        assert mock_get_project_info.call_count == 1
        assert mock_get_member_info.call_count == 1
        assert mock__extract_and_insert_metadata.call_count == 2

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[0][0][2]
        assert schema_property_arg == "researcher[].email[]"

        schema_property_arg = mock__extract_and_insert_metadata.call_args_list[1][0][2]
        assert schema_property_arg == "researcher[].affiliation[].name"

    def test_mapping_metadata_3(self, mocker):

        filter_property = ["researcher.affiliation.adress", "researcher.affiliation.name"]
        mock_mapping_definition = {
            "researcher[].affiliation[].adress[]": {
                "type": "string",
                "value": None
            },
            "researcher[].affiliation[].name": {
                "type": "string",
                "value": None,
            }
        }
        mock_metadata_sources = []
        mock_source_data = {}
        mock_new_schema = {
            "researcher": [
                {
                    "affiliation": [
                        {
                            "adress": [],
                            "name": None
                        }
                    ]
                }
            ]
        }

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=mock_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=mock_metadata_sources)
        mock__add_property = mocker.patch(
            "dg_mm.models.grdm.GrdmMapping._add_property", return_value=mock_new_schema)

        target_class = GrdmMapping()
        metadata = target_class.mapping_metadata(
            "リサーチフロー", "valid_token", "valid_project_id", filter_property)

        assert isinstance(metadata, dict)
        assert metadata == mock_new_schema

        assert mock__add_property.call_count == 2

        schema_property_arg = mock__add_property.call_args_list[0][0][1]
        assert schema_property_arg == "researcher[].affiliation[].adress[]"

        schema_property_arg = mock__add_property.call_args_list[1][0][1]
        assert schema_property_arg == "researcher[].affiliation[].name"

    def test_mapping_metadata_4(self, mocker):

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication", sode_effect=AuthenticationError("認証に失敗しました。"))

        target_class = GrdmMapping()

        with pytest.raises(AuthenticationError) as e:
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id")

        assert str(e.value) == "認証に失敗しました。"

    def test_mapping_metadata_5(self, mocker):

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=MappingDefinitionError("マッピング定義ファイルの読み込みに失敗しました。"))

        target_class = GrdmMapping()

        with pytest.raises(MappingDefinitionError) as e:
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id")

        assert str(e.value) == "マッピング定義ファイルの読み込みに失敗しました。"

    def test_mapping_metadata_6(self, mocker):

        filter_property = []

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=NotFoundKeyError("絞り込むプロパティが指定されていません。"))

        target_class = GrdmMapping()

        with pytest.raises(NotFoundKeyError) as e:
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id", filter_property)

        assert str(e.value) == "絞り込むプロパティが指定されていません。"

    def test_mapping_metadata_7(self, mocker):

        filter_property = ["non_existent_property"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", side_effect=NotFoundKeyError("指定したプロパティが存在しません。"))

        target_class = GrdmMapping()

        with pytest.raises(MappingDefinitionError) as e:
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id", filter_property)

        assert str(e.value) == "指定したプロパティが存在しません。"

    def test_mapping_metadata_8(self, mocker):

        mock_metadata_sources = [
            "project_info", "member_info", "project_metadata", "file_metadata"]

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition")
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=mock_metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_project_info", side_effect=Exception("メタデータの取得に失敗しました。"))

        target_class = GrdmMapping()

        with pytest.raises(Exception) as e:
            target_class.mapping_metadata(
                "リサーチフロー", "invalid_token", "invalid_project_id")

        assert str(e.value) == "メタデータの取得に失敗しました。"

    def test_mapping_metadata_9(self, mocker):

        mock_mapping_definition = {
            "researcher[].email[]": {
                "type": "string",
                "source": "member_info",
                "value": "data.embeds.users.data.attributes.email",
                "list": {
                    "data": "researcher"
                }
            },
            "researcher[].affiliation[].name": {
                "type": "string",
                "source": "member_info",
                "value": "data.embeds.users.data.attributes.employment.institution_ja",
                "list": {
                    "data": "researcher",
                    "employment": "affiliation"
                }
            }
        }
        mock_metadata_sources = ["member_info"]
        mock_source_data = {}
        mock_new_schema = {
            "researcher": [
                {
                    "email": ["test_email"],
                    "affiliation": [
                        {
                            "adress": [],
                            "name": "test_name"
                        }
                    ]
                }
            ]
        }

        mocker.patch("dg_mm.models.grdm.GrdmAccess.check_authentication")
        mocker.patch("dg_mm.models.mapping_definition.DefinitionManager.get_and_filter_mapping_definition", return_value=mock_mapping_definition)
        mocker.patch("dg_mm.models.grdm.GrdmMapping._find_metadata_sources", return_value=mock_metadata_sources)
        mocker.patch("dg_mm.models.grdm.GrdmAccess.get_member_info", return_value=mock_source_data)
        mock__extract_and_insert_metadata = mocker.patch(
            "dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect=MappingDefinitionError("マッピングに失敗しました。"))

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError)as e:
            target_class.mapping_metadata(
                "リサーチフロー", "valid_token", "valid_project_id",)

        assert mock__extract_and_insert_metadata.call_count == 1
        assert str(e.value) == "マッピングに失敗しました。"

    def test__find_metadata_sources_1(self):
        test_mapping_definition = {
            "researcher[].email[]": {
                "type": "string",
                "source": "project_info",
                "value": "data.embeds.users.data.attributes.email",
                "list": {
                    "data": "researcher"
                }
            },
            "researcher[].affiliation[].adress[]": {
                "type": "string",
                "source": "project_info",
                "value": None
            },
            "researcher[].affiliation[].name": {
                "type": "string",
                "source": "member_info",
                "value": "data.embeds.users.data.attributes.employment.institution_ja",
                "list": {
                    "data": "researcher",
                    "employment": "affiliation"
                }
            }
        }
        expected_metadata_sources = ["project_info", "member_info"]
        target_class = GrdmMapping()
        target_class._mapping_definition = test_mapping_definition
        metadata_sources = target_class._find_metadata_sources()

        assert Counter(metadata_sources) == Counter(expected_metadata_sources)

    def test__find_metadata_sources_2(self):
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

        assert metadata_sources == []

    def test__extract_and_insert_metadata_1(self):
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
                "sc2": "value1"
            }
        }
        target_class = GrdmMapping()
        new_schema = target_class._extract_and_insert_metadata(
            new_schema, sources, schema_property, components, schema_link_list, storage_keys)

        assert new_schema == excepted_schema

    def test__extract_and_insert_metadata_3(self):
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
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2", "st3"]
        schema_property = "sc1.sc2"
        components = {
            "type": "nubmber",
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
                        "st3": "value1"
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
                                "sc4": "value1"
                            }
                        },
                        {
                            "st3": {
                                "sc4": "value2"
                            }
                        }
                    ]
                },
                {
                    "st2": [
                        {
                            "st3": {
                                "sc4": "value3"
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

        assert str(e.value) == f"マッピング定義に誤りがあります({schema_property})"

    def test__extract_and_insert_metadata_18(self):
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
                                "sc4": "value1",
                                "sc5": "value2"
                            }
                        },
                        {
                            "st3": {
                                "sc4": "value3",
                                "sc5": "value4"
                            }
                        }
                    ]
                },
                {
                    "st2": [
                        {
                            "st3": {
                                "sc4": "value5",
                                "sc5": "value6"
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
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st0", "st2"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3",
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

        assert str(e.value) == f"st1と一致するストレージのキーが見つかりませんでした。({schema_property})"

    def test__check_and_handle_key_structure_2(self):
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st0", "st2"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2.st3",
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

        assert str(e.value) == f"st1と一致するストレージのキーが見つかりませんでした。({schema_property})"

    def test__handle_list_1(self, mocker):
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
                        "st3": "value2"
                    },
                    "st4": "value3"
                }
            ]
        }
        index = 0
        key = "st1[]"

        mocker.patch("dg_mm.models.grdm.GrdmMapping._extract_and_insert_metadata", side_effect = NotFoundKeyError(f"st2と一致するストレージのキーが見つかりませんでした。({schema_property})"))

        target_class = GrdmMapping()
        with pytest.raises(NotFoundKeyError) as e:
            result = target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert result is None
        assert e.value.args[0] == [f"st2と一致するストレージのキーが見つかりませんでした。({schema_property})"]

    def test__handle_list_2(self):
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

        target_class = GrdmMapping()
        with pytest.raises(MappingDefinitionError) as e:
            result = target_class._handle_list(
                new_schema, sources, schema_property, components, schema_link_list, storage_keys, index, key)

        assert result is None
        assert str(e.value) ==  f"指定されたインデックス:2が存在しません({schema_property})"

    def test__get_and_insert_final_key_value_1(self, mocker):
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
        schema_property = "sc1.sc2"
        components = {
            "type": "string",
            "source": "project_metadata",
            "value": "st1.st2",
        }
        source = {
            "st2": "value1"
        }
        final_key = "st2"

        added_schema ={
            "sc1" : {
                "sc2" :None
            }
        }

        mock__add_property = mocker.patch("dg_mm.models.grdm.GrdmMapping._add_property", return_value = added_schema)

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, storage_keys, final_key, schema_link_list)

        assert mock__add_property.call_count == 1
        assert new_schema == added_schema

    def test__get_and_insert_final_key_value_2(self, mocker):
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
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
        added_schema ={
            "sc1" :[
                {
                    "sc2" :"value1"
                },
                {
                    "sc2" : "value2"
                }
            ]
        }

        mock__add_property = mocker.patch("dg_mm.models.grdm.GrdmMapping._add_property", return_value = added_schema)

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, storage_keys, final_key, schema_link_list)

        assert mock__add_property.call_count == 2
        assert new_schema == added_schema

    def test__get_and_insert_final_key_value_3(self, mocker):
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
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
        added_schema ={
            "sc1" :{
                    "sc2" :"value1"
                }
        }

        mock__add_property = mocker.patch("dg_mm.models.grdm.GrdmMapping._add_property", return_value = added_schema)

        target_class = GrdmMapping()
        new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, storage_keys, final_key, schema_link_list)

        assert mock__add_property.call_count == 1
        assert new_schema == added_schema

    def test__get_and_insert_final_key_value_4(self):
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
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
            new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, storage_keys, final_key, schema_link_list)

        assert str(e.value) == f"指定されたインデックスが存在しません({schema_property})"

    def test__get_and_insert_final_key_value_5(self ):
        new_schema = {}
        schema_link_list = {}
        storage_keys = ["st1", "st2"]
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
            new_schema = target_class._get_and_insert_final_key_value(new_schema, source, schema_property, components, storage_keys, final_key, schema_link_list)

        assert str(e.value) == f"データ構造が定義と異なっています({schema_property})"

    def test__add_property_1(self, mocker):
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

        mock__convert_data_type = mocker.patch("dg_mm.models.grdm.GrdmMapping._convert_data_type", return_value = storage_data)

        target_class = GrdmMapping()
        new_schema = target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert mock__convert_data_type.call_count == 1
        assert new_schema == expected_schema

    def test__add_property_2(self):
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

    def test__add_property_3(self):
        new_schema = {
            "sc1" :[
                {
                    "sc2" : "value1"
                },
                {
                    "sc2" : "value2"
                },
            ]
        }
        schema_property = "sc1[].sc3"
        type = "string"
        storage_data = ["value3"]
        schema_link_list = {}

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert str(e.value) == f"マッピング定義に誤りがあります({schema_property})"

    def test__add_property_4(self, mocker):
        new_schema = {}
        schema_property = "sc1.sc2"
        type = "invalid_type"
        storage_data = ["value1"]
        schema_link_list = {}

        mock__convert_data_type = mocker.patch("dg_mm.models.grdm.GrdmMapping._convert_data_type", side_effect = MappingDefinitionError)

        with pytest.raises(MappingDefinitionError) as e:
            target_class = GrdmMapping()
            target_class._add_property(new_schema, schema_property, type, storage_data, schema_link_list)

        assert mock__convert_data_type.call_count == 1
        assert str(e.value) == f"type:{type}は有効な型ではありません({schema_property})"

    def test__convert_data_type_1():
        data =[True, False]
        type = "string"

        excepted_data = ["True", "False"]

        target_class = GrdmMapping()
        converted_data =target_class._convert_data_type(data, type)

        assert converted_data == excepted_data

    def test__convert_data_type_2():
        data =[]
        type = "string"

        excepted_data = ["True", "False"]

        target_class = GrdmMapping()
        converted_data =target_class._convert_data_type(data, type)

        assert converted_data == excepted_data













