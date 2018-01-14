from AutomatedRedistricting.util import util

class DistrictBuilder:

    def __init__(self,layer):
        attributes = util.loadYaml('model','poliline_attributes.yaml','attributes')
        self.feature_dict_poliline = {f[attributes['id_poliline']]: f for f in layer.getFeatures()}

    def perimeter(self,units):
            units=set(units)
            borders=set()

            for unit in units:
                borders^=unit.lines

            perimeter=0
            for border in borders:
            #search for border lines
                perimeter+=self.feature_dict_poliline[int(border)].geometry().length()

            return perimeter

    def setGeo(self,district):
        #create district formed by units in unitlist

        district.perimeter = self.perimeter(district.units)

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
