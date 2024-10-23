
from typing import Any
from dg_mm.models.base import BaseMapping

class DummyMapping():

    def mapping_metadata(self, schema: str, *args: Any, **kwargs: Any):
        pass

class TestBaseMapping():
    def test_mapping_metadata(self):
        dummy_class : BaseMapping = DummyMapping()

        result = dummy_class.mapping_metadata("test_schema", "test_token", "test_project_id")

        assert result is None



