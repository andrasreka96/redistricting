from qgis.core import *
from model import Unit,District
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import random
from log_conf import Logger

class QgsRandomColorScheme(QgsColorScheme):
    def __init__(self, parent=None):
        QgsColorScheme.__init__(self)

    def fetchColors(self, noColors,basecolor=QColor() ):
        minVal = 130;
        maxVal = 255;
        colorList = []
        for i in range(noColors):
            if basecolor.isValid():
                h = basecolor.hue()
            else:
                #generate random hue
                h = random.randrange(360);

            s = random.randrange(100,255)
            v = random.randrange(100,255)

            colorList.append(QColor.fromHsv( h, s, v).name())

        return colorList

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
        # Create a dictionary of all features
        Logger.logr.info("Hello")
        feature_dict = {f['natcode']: f for f in self.layer.getFeatures()}
        perimiter=0;
        area=0;
        population=0;
        #self.layer.startEditing()
        #for unit in unitlist:
        #        f=feature_dict[unit.getID()]
        #        f['color']=color
        #        self.layer.updateFeature(f)

        #logging.info("Changes has beens saved in district %s",id)
        #self.layer.commitChanges()
        return District(id,color,unitlist,perimiter,area,population)
