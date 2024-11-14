import pytest

from dg_mm.errors import (
    InvalidIdError,
    InvalidStorageError,
    InvalidTokenError,
    KeyNotFoundError,
    MappingDefinitionNotFoundError
)
from dg_mm.models.metadata_manager import MetadataManager


class TestMetadataManager:
    def test_get_metadata_success_1(self, mocker):
        """スキーマ全体を取得"""

        # モック化
        mock_obj = mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", return_value={"key: value"})

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
        assert result == {"key: value"}
        mock_obj.assert_called_with(schema="RF", token="valid", project_id="valid",
                                    filter_properties=None, project_metadata_id=None)

    def test_get_metadata_success_2(self, mocker):
        """スキーマの一部を取得"""

        # モック化
        mock_obj = mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", return_value={"key: value"})

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": ["valid_property"]
        }
        target_class = MetadataManager()
        result = target_class.get_metadata(**param)

        # 結果の確認
        assert result == {"key: value"}
        mock_obj.assert_called_with(schema="RF", token="valid", project_id="valid",
                                    filter_properties=["valid_property"], project_metadata_id=None)

    def test_get_metadata_failure_1(self, mocker):
        """対応していないスキーマを指定"""

        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=MappingDefinitionNotFoundError)

        # テスト実行
        param = {
            "schema": "invalid",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid"
        }
        target_class = MetadataManager()
        with pytest.raises(MappingDefinitionNotFoundError):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_2(self):
        """対応していないストレージを指定"""

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "invalid",
            "token": "valid",
            "id": "valid"
        }
        target_class = MetadataManager()
        with pytest.raises(InvalidStorageError, match="対応していないストレージが指定されました。"):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_3(self, mocker):
        """トークンを指定しない"""

        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=InvalidTokenError)

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "id": "valid"
        }
        target_class = MetadataManager()
        with pytest.raises(InvalidTokenError):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_4(self, mocker):
        """プロジェクトIDを指定しない"""

        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=InvalidIdError)

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
        }
        target_class = MetadataManager()
        with pytest.raises(InvalidIdError):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_5(self, mocker):
        """オプション(取得するプロパティ一覧)が空"""

        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=KeyNotFoundError)

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": []
        }
        target_class = MetadataManager()
        with pytest.raises(KeyNotFoundError):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_6(self, mocker):
        """スキーマに存在しないプロパティをオプションに指定"""

        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=KeyNotFoundError)

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": ["invalid_property"]
        }
        target_class = MetadataManager()
        with pytest.raises(KeyNotFoundError):
            target_class.get_metadata(**param)
