from typing import Dict, Any
import importlib
from dg_mm.error import NotExistID
from nii_dg.entity import Entity

class EntityInfo():

    def __init__(self, schema_name:str, entity_name:str, props:Dict[str, Any]) -> None:
        self._schema_name = schema_name
        self._entity_name = entity_name
        self._props = props

    def get_ref_id(self)->Dict[str, Any]:
        ref_id = {}
        has_id = False
        for k, v in self._props.items():
            if k == '@id':
                ref_id[k] = v
                has_id = True
        if not has_id:
            raise NotExistID(f'This EntityInfo instance does not have @id. schema_name : {self._schema_name}, entity_name : {self._entity_name}, props : {self._props}')
        return ref_id

    def generate_entity(self)->Entity:
        # import module
        module = importlib.import_module(f"nii_dg.schema.{self._schema_name}")
        # get class
        class_ = getattr(module, self._entity_name)
        props = {}
        has_id = False
        for key, value in self._props.items():
            if key == '@id':
                has_id = True
            else:
                props[key] = value
        if has_id:
            instance = class_(id_=self._props['@id'], props=props)
        else:
            instance = class_(props=props)
        return instance

    @classmethod
    def generate_entity_by_schema_entity(cls, schema_name:str, entity_name:str, props:Dict[str, Any])->Entity:
        ei = EntityInfo(schema_name, entity_name, props)
        return ei.generate_entity()