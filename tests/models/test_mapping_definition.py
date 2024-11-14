"""mappyng_definition.pyをテストするためのモジュールです。"""
import pytest

from dg_mm.errors import (MappingDefinitionError, KeyNotFoundError, MappingDefinitionNotFoundError)
from dg_mm.models.mapping_definition import DefinitionManager


class TestDefinitionManager():
    """DefinitionManagerクラスのテストを行うクラスです。"""

    def test_get_and_filter_mapping_definition_1(self, mocker, read_test_mapping_definition):
        """(正常系テスト 41）filter_propertiesを指定せず、全マッピング定義を取得するテストケースです。"""

        schema = "RF"
        storage = "GRDM"
        # テスト用のマッピング定義を取得
        test_mapping_definition = read_test_mapping_definition["base_mapping_definition"]

        # _read_mapping_definitionをモック化
        mock__read_mapping_definition = mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value=test_mapping_definition)

        # テストを実行
        target_class = DefinitionManager()
        mapping_definition = target_class.get_and_filter_mapping_definition(schema, storage)

        # 結果を検証
        assert mock__read_mapping_definition.call_count == 1
        assert mapping_definition == test_mapping_definition

    def test_get_and_filter_mapping_definition_2(self, mocker, read_test_mapping_definition):
        """(正常系テスト 42)filter_propertiesで指定したプロパティで絞り込んだマッピング定義を取得するテストケースです。

        プロパティを末端のキーまで指定して絞り込みを行います。

        """
        schema = "RF"
        storage = "GRDM"
        # 絞り込みに用いるスキーマのプロパティ
        filter_properties = ["researcher.email", "researcher.affiliation.name"]

        # テスト用のマッピング定義を取得
        test_mapping_definition = read_test_mapping_definition["base_mapping_definition"]
        # テストを実行した場合に期待される絞り込まれたマッピング定義を取得
        expected_mapping_definition = read_test_mapping_definition["test_get_and_filter_mapping_definition_2"]

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value=test_mapping_definition)

        target_class = DefinitionManager()
        mapping_definition = target_class.get_and_filter_mapping_definition(schema, storage, filter_properties)

        assert mapping_definition == expected_mapping_definition

    def test_get_and_filter_mapping_definition_3(self, mocker, read_test_mapping_definition):
        """(正常系テスト 42)filter_propertiesで指定したプロパティで絞り込んだマッピング定義を取得するテストケースです。

        プロパティの途中のキーまでを指定して絞り込みを行います。

        """
        schema = "RF"
        storage = "GRDM"
        filter_properties = ["researcher.affiliation"]

        test_mapping_definition = read_test_mapping_definition["base_mapping_definition"]
        expected_mapping_definition = read_test_mapping_definition["test_get_and_filter_mapping_definition_3"]

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value=test_mapping_definition)

        target_class = DefinitionManager()
        mapping_definition = target_class.get_and_filter_mapping_definition(schema, storage, filter_properties)

        assert mapping_definition == expected_mapping_definition

    def test_get_and_filter_mapping_definition_4(self, mocker):
        """(異常系テスト 41)対応していないスキーマを指定された場合のテストケースです。"""
        # 不正なスキーマを指定
        schema = "invalid_schema"
        storage = "GRDM"

        # _read_mapping_definitionがNotFoundMappingDefinitionErrorを返すようにモック化
        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            side_effect=MappingDefinitionNotFoundError("マッピング定義ファイルが見つかりません。"))

        with pytest.raises(MappingDefinitionNotFoundError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルが見つかりません。"

    def test_get_and_filter_mapping_definition_5(self, mocker):
        """(異常系テスト 42)対応していないストレージを指定された場合のテストケースです。"""

        # 不正なストレージを指定
        schema = "RF"
        storage = "invalid_storage"

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            side_effect=MappingDefinitionNotFoundError("マッピング定義ファイルが見つかりません。"))

        with pytest.raises(MappingDefinitionNotFoundError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルが見つかりません。"

    def test_get_and_filter_mapping_definition_6(self, mocker):
        """(異常系テスト 43)ファイルの読み込みに失敗した場合のテストケースです。"""
        schema = "RF"
        storage = "GRDM"

        # _read_mapping_definitionがMappingDefinitionErrorを返すようにモック化
        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            side_effect=MappingDefinitionError("マッピング定義ファイルの読み込みに失敗しました。"))

        with pytest.raises(MappingDefinitionError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルの読み込みに失敗しました。"

    def test_get_and_filter_mapping_definition_7(self, mocker, read_test_mapping_definition):
        """(異常系テスト)filter_propertiesで存在しないプロパティを指定した場合のテストケースです。"""
        schema = "RF"
        storage = "GRDM"
        # 存在しないプロパティを指定
        filter_properties = ["non_existent_property"]

        test_mapping_definition = read_test_mapping_definition["base_mapping_definition"]

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value=test_mapping_definition)

        with pytest.raises(KeyNotFoundError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage, filter_properties)

        assert str(e.value) == "指定したプロパティ: ['non_existent_property'] が存在しません。"

    def test_get_and_filter_mapping_definition_8(self, mocker, read_test_mapping_definition):
        """(異常系テスト)filter_propertiesが空のリストとして渡された場合のテストケースです。"""
        schema = "RF"
        storage = "GRDM"
        # 空のプロパティ
        filter_properties = []

        test_mapping_definition = read_test_mapping_definition["base_mapping_definition"]

        mocker.patch(
            "dg_mm.models.mapping_definition.DefinitionManager._read_mapping_definition",
            return_value=test_mapping_definition)

        with pytest.raises(KeyNotFoundError) as e:
            target_class = DefinitionManager()
            target_class.get_and_filter_mapping_definition(schema, storage, filter_properties)

        assert str(e.value) == "絞り込むプロパティが指定されていません。"

    def test__read_mapping_definition_1(self, create_test_definition):
        """(正常系テスト 43)Json形式のマッピング定義ファイルを読み込むテストケースです。"""
        # 検証用の期待されるマッピング定義
        expected_schema = {"test_property": {"test_definition": "value"}}

        # テストを実行
        target_class = DefinitionManager()
        mapping_definition = target_class._read_mapping_definition(*create_test_definition)

        # 検証
        assert mapping_definition == expected_schema

    def test__read_mapping_definition_2(self):
        """(異常系テスト 44)指定したスキーマ、ストレージに対応したファイルが存在しない場合のテストケースです。"""

        # 不正なスキーマ、ストレージを指定
        schema = "invalid_schema"
        storage = "invalid_storage"

        with pytest.raises(MappingDefinitionNotFoundError)as e:
            target_class = DefinitionManager()
            target_class._read_mapping_definition(schema, storage)

        assert str(e.value) == "マッピング定義ファイルが見つかりません。"

    def test__read_mapping_definition_3(self, create_invalid_test_definition):
        """(異常系テスト 45)マッピング定義ファイルがjson形式ではないため、読み込みに失敗した場合のテストケースです。

        ファイルの内容がjson形式ではないマッピング定義ファイルを作成し、それを読み取るように設定します。

        """
        # MappingDefinitionErrorをキャッチするようにしてテストを実行
        with pytest.raises(MappingDefinitionError) as e:
            target_class = DefinitionManager()
            target_class._read_mapping_definition(*create_invalid_test_definition)

        assert str(e.value) == "マッピング定義ファイルの読み込みに失敗しました。"
