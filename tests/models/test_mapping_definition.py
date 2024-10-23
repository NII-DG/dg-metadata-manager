import json
import pytest
from json import JSONDecodeError

from dg_mm.exceptions import MappingDefinitionError, NotFoundKeyError, NotFoundMappingDefinitionError
from dg_mm.models.mapping_definition import DefinitionManager


class TestDefinitionManager():
    """DefinitionManagerクラスのテストを行うクラスです。"""

    #テストを行う為の仮のマッピング定義
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

    def test_get_and_filter_mapping_definition_1(self, mocker):
        """filter_propertyを指定せず、全マッピング定義を取得する正常系のテストケースです。"""

        schema = "RF"
        storage = "GRDM"

        #_read_mapping_definitionをモック化
        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value = TestDefinitionManager.mock_mapping_definition )

        #テストを実行
        target_class = DefinitionManager()
        mapping_definition = target_class.get_and_filter_mapping_definition(schema, storage)

        #結果を検証
        assert isinstance(mapping_definition, dict)
        assert mapping_definition == TestDefinitionManager.mock_mapping_definition

    def test_get_and_filter_mapping_definition_2(self, mocker):
        """filter_propertyで指定したプロパティで絞り込んだマッピング定義を取得する正常系のテストケースです。

        プロパティを末端のキーまで指定して絞り込みを行います。

        """
        schema = "RF"
        storage = "GRDM"
        #絞り込みに用いるスキーマのプロパティ
        filter_property = ["researcher.email", "researcher.affiliation.name" ]
        #テストを実行した場合に期待される絞り込まれたマッピング定義
        expected_filterd_mapping_definition = {
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

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value = TestDefinitionManager.mock_mapping_definition )


        target_class = DefinitionManager()
        mapping_definition = target_class.get_and_filter_mapping_definition(schema, storage, filter_property)

        assert isinstance(mapping_definition, dict)
        assert mapping_definition == expected_filterd_mapping_definition

    def test_get_and_filter_mapping_definition_3(self, mocker):
        """filter_propertyで指定したプロパティで絞り込んだマッピング定義を取得する正常系のテストケースです。

        プロパティの途中のキーまでを指定して絞り込みを行います。

        """
        schema = "RF"
        storage = "GRDM"
        filter_property = ["researcher.affiliation" ]
        expected_filterd_mapping_definition = {
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

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value = TestDefinitionManager.mock_mapping_definition )

        target_class = DefinitionManager()
        mapping_definition = target_class.get_and_filter_mapping_definition(schema, storage, filter_property)

        assert isinstance(mapping_definition, dict)
        assert mapping_definition == expected_filterd_mapping_definition

    def test_get_and_filter_mapping_definition_4(self, mocker):
        """対応していないスキーマを指定された場合の異常系テストケースです。"""
        #不正なスキーマを指定
        schema = "invalid_schema"
        storage = "GRDM"

        #_read_mapping_definitionがNotFoundMappingDefinitionErrorを返すようにモック化
        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            side_effect = NotFoundMappingDefinitionError("マッピング定義ファイルが見つかりません。")
        )

        with pytest.raises(NotFoundMappingDefinitionError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルが見つかりません。"

    def test_get_and_filter_mapping_definition_5(self, mocker):
        """対応していないストレージを指定された場合の異常系テストケースです。"""
        #不正なストレージを指定
        schema = "RF"
        storage = "invalid_storage"

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            side_effect = NotFoundMappingDefinitionError("マッピング定義ファイルが見つかりません。")
        )

        with pytest.raises(NotFoundMappingDefinitionError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルが見つかりません。"


    def test_get_and_filter_mapping_definition_6(self, mocker):
        """ファイルの読み込みに失敗した場合の異常系テストケースです。"""
        schema = "RF"
        storage = "GRDM"

        #_read_mapping_definitionがMappingDefinitionErrorを返すようにモック化
        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            side_effect = MappingDefinitionError("マッピング定義ファイルの読み込みに失敗しました。")
        )

        with pytest.raises(NotFoundMappingDefinitionError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルの読み込みに失敗しました。"

    def test_get_and_filter_mapping_definition_7(self, mocker):
        """filter_propertyで存在しないプロパティを指定した場合の異常系テストケースです。"""
        schema = "RF"
        storage = "GRDM"
        #存在しないプロパティを指定
        filter_property = ["non_existent_property"]

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value = TestDefinitionManager.mock_mapping_definition )


        with pytest.raises(NotFoundKeyError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage, filter_property)

        assert str(e.value) == "指定したプロパティ: ['non_existent_property'] が存在しません"

    def test__read_mapping_definition_1(self, create_dummy_definition):
        """サンプルのテストケースです。"""
        with pytest.raises(JSONDecodeError):
            # テスト実行
            target_class = DefinitionManager()
            target_class._read_mapping_definition(*create_dummy_definition)

    def test__read_mapping_definition_2(self):
        """リサーチフロー、GRDMのマッピング定義ファイルを読み込む正常系のテストケースです。"""
        schema = "RF"
        storage = "GRDM"

        #テストを実行
        target_class = DefinitionManager()
        mapping_definition = target_class._read_mapping_definition(
            schema, storage)

        #検証のため、期待されるマッピング定義を取得
        file_path = f'../dg_mm/data/mapping/{storage}_{schema}_mapping.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            expected_result = json.load(f)

        #検証
        assert isinstance(mapping_definition, dict)
        assert mapping_definition == expected_result

    def test__read_mapping_definition_3(self):
        """指定したスキーマ、ストレージに対応したファイルが存在しない場合の異常系テストケースです。"""
        #不正なスキーマ、ストレージを指定
        schema = "invalid_schema"
        storage = "invalid_storage"

        #NotFoundMappingDefinitionErrorをキャッチするようにしてテストを実行
        with pytest.raises(NotFoundMappingDefinitionError)as e:
            target_class = DefinitionManager()
            target_class._read_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルが見つかりません。"

    def test__read_mapping_definition_4(self, create_invalid_dummy_definition):
        """マッピング定義ファイルがjson形式ではないため、読み込みに失敗した場合の異常系テストケースです。

        マッピング定義ファイルをtext形式で作成し、それを読み取るように設定します。

        """
        #MappingDefinitionErrorをキャッチするようにしてテストを実行
        with pytest.raises(MappingDefinitionError) as e:
            target_class = DefinitionManager()
            target_class._read_mapping_definition(*create_invalid_dummy_definition)

        assert str(e.value) == "マッピング定義ファイルの読み込みに失敗しました。"
