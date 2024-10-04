import pytest
from json import JSONDecodeError

from dg_mm.models.mapping_definition import DefinitionManager


class TestDefinitionManager():
    def test__read_mapping_definition_1(self, create_dummy_definition):
        with pytest.raises(JSONDecodeError):
            # テスト実行
            target_class = DefinitionManager()
            target_class._read_mapping_definition(*create_dummy_definition)