from unittest import TestCase
from dg_mm.packaging import EntityInfo
from dg_mm.error import NotExistID

class TestEntityInfo(TestCase):

    def test_constructor(self):
        # Case:1 Entity information with ID
        schema_name_1 = 'test schema_name_1'
        entity_name_1 = 'test entity_name_1'
        props_1 = {
            '@id' : 'test id 1',
            'name' : 'data name_1'
            }
        ei_1 = EntityInfo(schema_name_1, entity_name_1, props_1)

        self.assertEqual(schema_name_1, ei_1._schema_name)
        self.assertEqual(entity_name_1, ei_1._entity_name)
        self.assertEqual(props_1, ei_1._props)

        # Case:2 Entity information without ID
        schema_name_2 = 'test schema_name_2'
        entity_name_2 = 'test entity_name_2'
        props_2 = {
            'name' : 'data name_2'
            }
        ei_2 = EntityInfo(schema_name_2, entity_name_2, props_2)

        self.assertEqual(schema_name_2, ei_2._schema_name)
        self.assertEqual(entity_name_2, ei_2._entity_name)
        self.assertEqual(props_2, ei_2._props)

    def test_get_ref_id_ok(self):
        schema_name_1 = 'test schema_name_1'
        entity_name_1 = 'test entity_name_1'
        id = 'test id 1'
        props_1 = {
            '@id' : id,
            'name' : 'data name_1'
            }
        ei_1 = EntityInfo(schema_name_1, entity_name_1, props_1)

        ref_id = ei_1.get_ref_id()
        self.assertEqual({'@id' : id}, ref_id)

    def test_get_ref_id_err(self):
        schema_name_1 = 'test schema_name_1'
        entity_name_1 = 'test entity_name_1'
        props_1 = {
            'name' : 'data name_1'
            }
        ei_1 = EntityInfo(schema_name_1, entity_name_1, props_1)

        expected_err_msg = f'This EntityInfo instance does not have @id. schema_name : {schema_name_1}, entity_name : {entity_name_1}, props : {props_1}'
        with self.assertRaises(NotExistID, msg=expected_err_msg):
            ref_id = ei_1.get_ref_id()
