from unittest import TestCase
from dg_mm.packaging import EntityInfo, Packager

class TestPackager(TestCase):

    def test_constructor(self):
        ro_name = 'test ro_name'
        entities = []
        ei_1 = EntityInfo('base', 'File', props={
            '@id' : './test_1.txt',
        })
        entities.append(ei_1)
        pkg = Packager(ro_name, entities)

        self.assertEqual(ro_name, pkg._ro_crate.root['name'])
        self.assertEqual(ei_1, pkg._entities[0])

    def test_add_entity(self):

        ro_name = 'test ro_name'
        entities = []
        ei_1 = EntityInfo('base', 'File', props={
            '@id' : './test_1.txt',
        })
        entities.append(ei_1)
        pkg = Packager(ro_name, entities)

        ei_2 = EntityInfo('base', 'File', props={
            '@id' : './test_2.txt',
        })
        pkg.add_entity(ei_2)

        self.assertEqual(ro_name, pkg._ro_crate.root['name'])
        self.assertEqual(ei_1, pkg._entities[0])
        self.assertEqual(ei_2, pkg._entities[1])

    def test_extend_entitys(self):

        ro_name = 'test ro_name'
        entities = []
        ei_1 = EntityInfo('base', 'File', props={
            '@id' : './test_1.txt',
        })
        entities.append(ei_1)
        pkg = Packager(ro_name, entities)

        ei_2 = EntityInfo('base', 'File', props={
            '@id' : './test_2.txt',
        })
        ei_3 = EntityInfo('base', 'File', props={
            '@id' : './test_3.txt',
        })

        pkg.extend_entitys([ei_2, ei_3])

        self.assertEqual(ro_name, pkg._ro_crate.root['name'])
        self.assertEqual(ei_1, pkg._entities[0])
        self.assertEqual(ei_2, pkg._entities[1])
        self.assertEqual(ei_3, pkg._entities[2])


    def test_package_to_ro_crate(self):
        ro_name = 'test ro_name'
        pkg = Packager(ro_name)

        fei_0 = EntityInfo(
            'base',
            'File',
            {
                '@id' : './test_0.txt',
                'name' : 'test_0.txt',
                'contentSize' : '1560B',
                'encodingFormat' : 'text/plain',
                'sha256' : 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                'url' : 'https://github.com/username/repository/file',
                'sdDatePublished' : '2022-12-01'
            }
        )
        pkg.add_entity(fei_0)
        fei_1 = EntityInfo(
            'ginfork',
            'File',
            {
                '@id' : './test_1.txt',
                'name' : 'test_1.txt',
                'contentSize' : '1560B',
                'encodingFormat' : 'text/plain',
                'sha256' : 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                'url' : 'https://github.com/username/repository/file',
                'sdDatePublished' : '2022-12-01',
                'experimentPackageFlag' : True
            }
        )
        pkg.add_entity(fei_1)
        base_org_1 = EntityInfo(
            'base',
            'Organization',
            {
                '@id' : 'https://ror.org/04ksd4g47',
                'name' : 'National Institute of Informatics',
                'alias' : 'NII',
                'description' : 'Japan\'s only general academic research institution seeking to create future value in the new discipline of informatics.'
            })
        pkg.add_entity(base_org_1)

        base_person_1 = EntityInfo(
            'base',
            'Person',
            {
                '@id' : 'https://orcid.org/0000-0001-2345-6789',
                'name' : 'Ichiro Suzuki',
                'affiliation' : base_org_1.get_ref_id(),
                'email' : 'ichiro@example.com'
            })
        pkg.add_entity(base_person_1)

        gin_ei = EntityInfo(
            'ginfork',
            'GinMonitoring',
            {
                'about' : pkg._ro_crate.root,
                'contentSize' : '100GB',
                'workflowIdentifier' : 'basic',
                'datasetStructure' : 'with_code',
                'experimentPackageList' : ["experiments/exp1/", "experiments/exp2/"],
                'parameterExperimentList' : [],
            }
        )
        pkg.add_entity(gin_ei)

        ro_crate = pkg.package_to_ro_crate()

        self.assertEqual(1, len(ro_crate.get_by_id(fei_0._props['@id'])))
        self.assertEqual(1, len(ro_crate.get_by_id(fei_1._props['@id'])))
        self.assertEqual(1, len(ro_crate.get_by_id(base_org_1._props['@id'])))
        self.assertEqual(1, len(ro_crate.get_by_id(base_person_1._props['@id'])))
        self.assertEqual(1, len(ro_crate.get_by_id('#ginmonitoring')))

        print(ro_crate.as_jsonld())
