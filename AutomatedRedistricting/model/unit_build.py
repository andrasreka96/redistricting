import os
import yaml
from AutomatedRedistricting.model.unit import Unit
import logging

class UnitBuilder:
    def __init__(self,features,attributes):
        self.attributes = attributes
        self.units = self.getUnits(features)
        self.dict_units = {u.id: u for u in self.units}
        self.setNeighbours()

    def getUnits(self,features):
        return  [Unit(feature[self.attributes['attribute_id']],
        feature[self.attributes['attribute_name']],feature[self.attributes['attribute_population']],
        feature[self.attributes['attribute_neighbours']].split(','),feature[self.attributes['attribute_lines']],feature.geometry().area()) for feature in features]

    def setNeighbours(self):
        #convert unit neighbours
        for unit in self.units:
            unit.neighbours= set(self.getUnitsById(unit.neighbours))

    def getUnitsById(self,id_list):
        #look for units with ids corresponding to id_list
        return [self.dict_units[id] for id in id_list if id in self.dict_units]

    def getUnitIds(self,units):
        return set([unit.id for unit in units])

    def getUnitById(self,id):
        return self.dict_units[id]
