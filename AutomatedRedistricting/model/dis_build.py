import logging
from AutomatedRedistricting.model.district import District

class DistrictBuilder:

    def __init__(self,layer,attribute_id_poliline):

        #create a dictionary of polilines
        self.feature_dict_poliline = {f[attribute_id_poliline]: f for f in layer.getFeatures()}


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

        district.perimeter = self.Perimeter(district.units)

        area=0;
        population=0;

        for unit in district.units:
        #distirict calculations
            area+=unit.area
            population+=unit.population

        district.area=area
        district.population=population

    def BuildDistrictFromUnits(self,id,unitlist,color,county):
        return District(id,unitlist,color)
