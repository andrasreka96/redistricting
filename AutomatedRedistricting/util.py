from qgis.core import *
from model import Unit,District
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import random
import logging
from layer_manipulation import LayerManipulation
import ast

class QgsRandomColorScheme(QgsColorScheme):
    def __init__(self, parent=None):
        QgsColorScheme.__init__(self)

    def fetchColors(self, noColors):
        return [QColor.fromRgb(random.randrange(100,255),random.randrange(100,255),random.randrange(100,255)).name() for _ in range(noColors) ]

class Util:

    ATTRIBUTE_NAME='name'
    ATTRIBUTE_POPULATION='pop2015'
    ATTRIBUTE_ID='natcode'
    ATTRIBUTE_ID_POLILINE='id'
    ATTRIBUTE_NEIGHBOURS='neighbours'
    ATTRIBUTE_LINES='lines'

    def __init__(self,features=None,layer=None,layer2=None):
        #save layers and dictionaries for them
        self.layer_poligon=layer
        self.feature_dict_poligon = {f[self.ATTRIBUTE_ID]: f for f in layer.getFeatures()}

        self.layer_poliline=layer2
        self.feature_dict_poliline = {f[self.ATTRIBUTE_ID_POLILINE]: f for f in layer2.getFeatures()}

        #list of Units
        if features:
            self.units = self.getUnits(features)
        else:
            self.units = self.getUnits(layer.getFeatures())


    def where(self,exp):
        exp=QgsExpression(exp)
        if exp.hasParserError()==0:
            exp.prepare(self.layer_poligon.pendingFields())
            for feature in self.layer_poligon.getFeatures():
                value = exp.evaluate(feature)
                if bool(value):
                    yield feature
#UnitBilder
    def getUnits(self,features):
        return  [Unit(feature,feature[self.ATTRIBUTE_ID],feature[self.ATTRIBUTE_NAME],feature[self.ATTRIBUTE_POPULATION],feature[self.ATTRIBUTE_NEIGHBOURS],feature[self.ATTRIBUTE_LINES],feature.geometry()) for feature in features]

    def getUnitsById(self,id_list):
        #look for units with ids corresponding to id_list
        return [unit for unit in self.units if unit.id in id_list]


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
            unit.district_id=district.id
            unit.color=district.color
        #distirict calculations
            area+=unit.area
            population+=unit.population

        perimeter = self.Perimeter(district.units)

        logging.info("\nDistrict %d\ncolor:%s\narea:%d\nperimiter:%d\npopulation:%d",district.id,district.color,area,perimeter,population)

        district.area=area
        district.perimeter=perimeter
        district.population=population

    def BuildDistrictFromUnits(self,id,unitlist,color):
        return District(id,unitlist,color)
