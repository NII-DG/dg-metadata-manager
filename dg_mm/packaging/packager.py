
from typing import List
from nii_dg.ro_crate import ROCrate
from dg_mm.packaging import EntityInfo
from nii_dg.entity import Entity

class Packager():

    def __init__(self, ro_name:str, entities:List[EntityInfo]=[]) -> None:
        ro_crate = ROCrate()
        ro_crate.root['name'] = ro_name
        self._ro_crate = ro_crate
        self._entities = entities

    def add_entity(self, entity:EntityInfo):
        self._entities.append(entity)

    def extend_entitys(self, entities:List[EntityInfo]):
        self._entities.extend(entities)

    def package(self)->ROCrate:
        ro_crate = self._ro_crate
        for entityinfo in self._entities:
            ro_crate.add(entityinfo.generate_entity())

        # Check each entity for excess or deficiency of properties
        ro_crate.as_jsonld()
        return ro_crate
