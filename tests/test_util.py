from dg_mm.util import PackageFileReader


class TestPackageFileReader():
    def test_is_file(self, create_dummy_file):
        assert PackageFileReader.is_file(create_dummy_file['file'])
        assert not PackageFileReader.is_file(create_dummy_file['dir'])
        assert not PackageFileReader.is_file(create_dummy_file['not_exist'])

    def test_read_json(self, create_dummy_json):
        json_obj = PackageFileReader.read_json(create_dummy_json)
        assert json_obj['key1'] == 'value1'

    def test_read_ini(self, create_dummy_ini):
        ini_obj = PackageFileReader.read_ini(create_dummy_ini)
        assert ini_obj['section1']['key1'] == 'value1'
