import pytest

from dg_mm.errors import InvalidProjectError, InvalidStorageError, InvalidTokenError, NotFoundKeyError, NotFoundMappingDefinitionError
from dg_mm.models.metadata_manager import MetadataManager

class TestMetadataManager:
    def test_get_metadata_success_1(mocker):
        # モック化
        mocker.patch()

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid"
        }
        target_class = MetadataManager()
        result = target_class.get_metadata(**param)

        # 結果の確認
        assert result

    def test_get_metadata_success_2():
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": []
        }
        target_class = MetadataManager()
        result = target_class.get_metadata(**param)

        # 結果の確認
        assert result

    def test_get_metadata_success_2():
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": []
        }
        target_class = MetadataManager()
        result = target_class.get_metadata(**param)

        # 結果の確認
        assert result

    def test_get_metadata_failure_1():
        # テスト実行
        param = {
            "schema": "invalid",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid"
        }
        target_class = MetadataManager()
        with pytest.raises(NotFoundMappingDefinitionError, match="マッピング定義ファイルが見つかりません。"):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_2():
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "invalid",
            "token": "valid",
            "id": "valid"
        }
        target_class = MetadataManager()
        with pytest.raises(InvalidStorageError, match="対応していないストレージが指定されました"):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_3():
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "id": "valid"
        }
        target_class = MetadataManager()
        with pytest.raises(InvalidTokenError, match="認証に失敗しました"):  # 本当はmapping_metadataではじいてほしい
            target_class.get_metadata(**param)

    def test_get_metadata_failure_4():
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
        }
        target_class = MetadataManager()
        with pytest.raises(InvalidProjectError, match="プロジェクトが存在しません"):    # 本当はmapping_metadataではじいてほしい
            target_class.get_metadata(**param)

    def test_get_metadata_failure_5():
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": []
        }
        target_class = MetadataManager()
        with pytest.raises(Exception, match=""):     # 不明。実装が違う
            target_class.get_metadata(**param)

    def test_get_metadata_failure_6():
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": ["invalid_property"]
        }
        target_class = MetadataManager()
        with pytest.raises(NotFoundKeyError, match=f"指定したプロパティ: invalid_property が存在しません"):
            target_class.get_metadata(**param)