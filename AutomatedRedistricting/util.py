from qgis.core import *
from model import Unit,District
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import random
import logging
from layer_manipulation import LayerManipulation

class QgsRandomColorScheme(QgsColorScheme):
    def __init__(self, parent=None):
        QgsColorScheme.__init__(self)

    def fetchColors(self, noColors):
        return [QColor.fromRgb(random.randrange(100,255),random.randrange(100,255),random.randrange(100,255)).name() for _ in range(noColors) ]

class Util:

    def __init__(self,layer):
        self.layer=layer

    def where(self,exp):
        exp=QgsExpression(exp)
        if exp.hasParserError()==0:
            exp.prepare(self.layer.pendingFields())
            for feature in self.layer.getFeatures():
                value = exp.evaluate(feature)
                if bool(value):
                    yield feature
#UnitBilder
    def getUnits(self,features,attribute_id,attribute_name,attribute_population,attribute_neighbours):
        return  [Unit(feature,feature[attribute_id],feature[attribute_name],feature[attribute_population],feature[attribute_neighbours],feature.geometry()) for feature in features]

    def getUnitsById(self,id_list,units):
        #look for units with ids corresponding to id_list
        return [unit for unit in units if unit.getID() in id_list]

#DistrictBilder
    def BuildDistrictFromUnits(self,id,unitlist,color):
        #create district formed by units in unitlist
        perimiter=0;
        area=0;
        population=0;
        for unit in unitlist:
            unit.setColor(color)
        return District(id,color,unitlist,perimiter,area,population)
