import os
import yaml
from AutomatedRedistricting.model.unit import Unit

class UnitBuilder:
    def __init__(self,features):
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)
        self.attributes = data.get('attributes')

        self.units = self.getUnits(features)
        self.dict_units = {u.id: u for u in self.units}

    def getUnits(self,features):
        return  [Unit(feature,feature[self.attributes['attribute_id']],
        feature[self.attributes['attribute_name']],feature[self.attributes['attribute_population']],
        feature[self.attributes['attribute_neighbours']],feature[self.attributes['attribute_lines']],feature.geometry()) for feature in features]

    def getUnitsById(self,id_list):
        #look for units with ids corresponding to id_list
        return [unit for unit in self.units if unit.id in id_list]
        #return [self.dict_units[int(id)] for id in id_list]

    def getUnitById(self,id):
        return self.dict_units[ids]
