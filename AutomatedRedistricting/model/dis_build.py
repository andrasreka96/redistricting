import os
import yaml
import logging
from AutomatedRedistricting.model.district import District

class DistrictBuilder:

    def __init__(self,layer):
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)

        self.attributes = data.get('attributes')

        #create a dictionary of polilines
        self.feature_dict_poliline = {f[self.attributes['attribute_id_poliline']]: f for f in layer.getFeatures()}


    def Perimeter(self,units):
        units=set(units)
        borders=set()

        for unit in units:
            borders^=unit.lines
        perimeter=0
        for border in borders:
        #search for border lines
            perimeter+=self.feature_dict_poliline[int(border)].geometry().length()

        return perimeter

    def BuildDistrict(self,district):
    #create district formed by units in unitlist
        area=0;
        population=0;
        perimeter=0;

        for unit in district.units:
        #distirict calculations
            area+=unit.area
            population+=unit.population

        perimeter = self.Perimeter(district.units)

        district.area=area
        district.perimeter=perimeter
        district.population=population

    def BuildDistrictFromUnits(self,id,unitlist,color,county):
        return District(id,unitlist,color)

    def RemoveDistrict(self,district,units):
        new_district = District(district.id,district.unique_id,district.color,district.units-units,population=district.population)
        self.BuildDistrict(new_district)
        return new_district

    def ExtandDistrict(self,district,units):
        new_district = District(district.id,district.unique_id,district.color,district.units+units,population=district.population)
        self.BuildDistrict(new_district)
        return new_district
