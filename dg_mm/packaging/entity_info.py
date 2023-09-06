from typing import Dict, Any
from dg_mm.error import NotExistID

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