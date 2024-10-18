from dg_mm.util import ReadPackageFile


class TestReadPackageFile():
    def test_read_json(self, create_dummy_json):
        json_obj = ReadPackageFile.read_json(create_dummy_json)
        assert json_obj['key1'] == 'value1'

    def test_read_ini(self, create_dummy_ini):
        ini_obj = ReadPackageFile.read_ini(create_dummy_ini)
        assert ini_obj['section1']['key1'] == 'value1'
