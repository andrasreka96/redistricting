from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging

class LayerManipulation:

    def __init__(self,layer):
        self.layer = layer
        self.feature_dict = {f['natcode']: f for f in layer.getFeatures()}

    def AddStringField(self,layer,fieldname):
        #add field to layer
        layer.startEditing()
        layer.dataProvider().addAttributes([QgsField(fieldname, QVariant.String)])
        layer.updateFields()

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

    def ColorDistricts(self,districts):
        self.layer.startEditing()
        for district in districts:
            logging.info("Coloring district:%d",district.id)
            for unit in district.units:
                f=self.feature_dict[unit.id]
                f['color']=district.color
                self.layer.updateFeature(f)
        self.layer.commitChanges()
        logging.info("Changes commited")

    def ChangeColor(self):
        renderer = QgsCategorizedSymbolRendererV2("natcode")
        self.layer.setRendererV2(renderer)
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        symbol.setColor(QColor(Qt.red))
        cat = QgsRendererCategoryV2(1, symbol, "1")
        renderer.addCategory(cat)
