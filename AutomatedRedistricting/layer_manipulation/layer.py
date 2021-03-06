from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging

class LayerManipulation:

    def __init__(self,layer):
        self.layer = layer
        self.feature_dict = {f['natcode']: f for f in layer.getFeatures()}

    def AddStringField(self,fieldname):
        #add field to layer
        self.layer.startEditing()
        self.layer.dataProvider().addAttributes([QgsField(fieldname, QVariant.String)])
        self.layer.updateFields()

#JoinPolilineToPoligon
    def Join(self,poliline,poligon):
        # Create new column for storing borderlines
        self.AddStringField(poligon,'lines')

        poligon.startEditing()
        #pair all lines with two poligon
        for line in poliline.getFeatures():
            line_id = str(line['id'])
            logging.info('Working on %s line',line_id)
            leftid = line['leftID']

            if leftid:
                f = self.feature_dict[leftid]
                if f['lines']:
                    str_ = str(f['lines']) + "," + line_id
                else:
                    str_ = line_id
                f['lines'] = str_
                poligon.updateFeature(f)


            rightid = line['rightID']
            if rightid:
                f = self.feature_dict[rightid]
                if f['lines']:
                    str_ = str(f['lines']) + "," + line_id
                else:
                    str_ = line_id
                f['lines'] = str_
                poligon.updateFeature(f)

        poligon.commitChanges()

    def ColorUnits(self,unitlist,color):
        logging.info("Coloring started")
        self.layer.startEditing()

        for unit in unitlist:
                f=self.feature_dict[unit.id]
                f['color']=color
                self.layer.updateFeature(f)

        self.layer.commitChanges()
        logging.info("Changes commited")

    def ColorFeature(self,feature,color):
        self.layer.startEditing()
        feature['color']=color
        self.layer.updateFeature(feature)
        self.layer.commitChanges()


    def ColorDistricts(self,counties,attribute):
        logging.info("Coloring %s",attribute)
        self.AddStringField(attribute)
        provider=self.layer.dataProvider()
        updateMap={}
        fieldIdx = provider.fields().indexFromName(attribute)
        features = provider.getFeatures()

        color_dict = {}
        for countie in counties:
            for district in countie.districts:
                for unit in district.units:
                    color_dict[unit.id]=district.color

        for feature in features:
            if feature['natcode'] in color_dict:
                updateMap[feature.id()] = { fieldIdx:color_dict[feature['natcode']] }

        provider.changeAttributeValues( updateMap )
        logging.info("Coloring %s done",attribute)

    def ChangeColor(self):
        renderer = QgsCategorizedSymbolRendererV2("natcode")
        self.layer.setRendererV2(renderer)
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        symbol.setColor(QColor(Qt.red))
        cat = QgsRendererCategoryV2(1, symbol, "1")
        renderer.addCategory(cat)
