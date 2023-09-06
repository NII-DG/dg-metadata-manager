
from typing import List
import importlib

from nii_dg.ro_crate import ROCrate
from dg_mm.packaging import EntityInfo
from dg_mm.error import InvalidInstanceType
class Packager():

    def __init__(self, ro_name:str) -> None:
        self._ro_name = ro_name
        self._entities = []

    def add_entity(self, entity:EntityInfo):
        self._entities.append(entity)

    def extend_entitys(self, entities:List[EntityInfo]):
        self._entities.extend(entities)

    def package_to_ro_crate(self)->ROCrate:
        ro_crate = ROCrate()
        ro_crate.root['name'] = self._ro_name

        for entity in self._entities:
            if type(entity) is not  EntityInfo:
                raise InvalidInstanceType('Instance type must be EntityInfo')

            # import module
            module = importlib.import_module(f"nii_dg.schema.{entity._schema_name}")
            # get class
            class_ = getattr(module, entity._entity_name)
            props = {}
            has_id = False
            for key, value in entity._props.items():
                if key == '@id':
                    has_id = True
                else:
                    props[key] = value
            if has_id:
                instance = class_(entity._props['@id'], props)
            else:
                instance = class_(props)
            ro_crate.add(instance)

        # Check each entity for excess or deficiency of properties
        ro_crate.as_jsonld()
        return ro_crate
