import json

import pytest

from dg_mm.errors import (
    InvalidProjectError,
    InvalidStorageError,
    InvalidTokenError,
    NotFoundKeyError,
    NotFoundMappingDefinitionError
)
from dg_mm.models.metadata_manager import MetadataManager


def read_json(path):
    with open(path, mode='r') as f:
        return json.load(f)


class TestMetadataManager:
    def test_get_metadata_success_1(self, mocker):
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
        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=NotFoundMappingDefinitionError)

        # テスト実行
        param = {
            "schema": "invalid",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid"
        }
        target_class = MetadataManager()
        with pytest.raises(NotFoundMappingDefinitionError):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_2(self):
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

    def test_get_metadata_failure_3(self, mocker):
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
        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=InvalidProjectError)

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
        }
        target_class = MetadataManager()
        with pytest.raises(InvalidProjectError):
            target_class.get_metadata(**param)

    def test_get_metadata_failure_5(self):
        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": []
        }
        target_class = MetadataManager()
        # エラーが出る実装になっていない
        with pytest.raises():
            target_class.get_metadata(**param)

    def test_get_metadata_failure_6(self, mocker):
        # モック化
        mocker.patch("dg_mm.models.grdm.GrdmMapping.mapping_metadata", side_effect=NotFoundKeyError)

        # テスト実行
        param = {
            "schema": "RF",
            "storage": "GRDM",
            "token": "valid",
            "id": "valid",
            "filter_properties": ["invalid_property"]
        }
        target_class = MetadataManager()
        with pytest.raises(NotFoundKeyError):
            target_class.get_metadata(**param)
