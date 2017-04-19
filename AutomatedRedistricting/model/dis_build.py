import os
import yaml
import logging
from AutomatedRedistricting.model.district import District

class DistrictBuilder:

    def __init__(self,layer):
        #save a dictionarie for polilines
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)

        self.attributes = data.get('attributes')
        self.feature_dict_poliline = {f[self.attributes['attribute_id_poliline']]: f for f in layer.getFeatures()}


    def Perimeter(self,units):
        #looks up for border lines
        units=set(units)
        borders=set()

        for unit in units:
            borders^=unit.lines
        perimeter=0
        for border in borders:
            perimeter+=self.feature_dict_poliline[int(border)].geometry().length()

        return perimeter

    def BuildDistrict(self,district):
        #create district formed by units in unitlist
        area=0;
        population=0;
        perimeter=0;

        for unit in district.units:
        #unit related settings
            #unit.district_id=district.unique_id
            #unit.color=district.color
        #distirict calculations
            area+=unit.area
            population+=unit.population

        perimeter = self.Perimeter(district.units)

        district.area=area
        district.perimeter=perimeter
        district.population=population

    def BuildDistrictFromUnits(self,id,unitlist,color,county):
        return District(id,unitlist,color,county)
