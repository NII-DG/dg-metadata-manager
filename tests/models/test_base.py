
from typing import Any
from dg_mm.models.base import BaseMapping


class DummyMapping():
    """プロトコルクラスをテストするためのダミークラスです。"""

    def mapping_metadata(self, schema: str, *args: Any, **kwargs: Any):
        """BaseMappingクラスに記載されている関数が実装できるか確かめるための関数です。"""
        return [schema, args, kwargs]


class TestBaseMapping():
    """BaseMappingクラスをテストするためのクラスです。"""

    def test_mapping_metadata(self):
        """mapping_metadataを実装できるか確かめるためのテストケースです。"""

        dummy_class: BaseMapping = DummyMapping()
        result = dummy_class.mapping_metadata("test_schema", "test_token", "test_project_id")

        assert result == ["test_schema", ("test_token", "test_project_id"), {}]
