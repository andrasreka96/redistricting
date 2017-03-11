from qgis.core import *
from PyQt4.QtCore import QVariant
import logging

class LayerManipulation:

    logging.basicConfig(format='%(asctime)s %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p',
                filename='/home/reka/Documents/redistricting/AutomatedRedistricting/log/LayerManipulation.log',
                filemode='w',
                level=logging.INFO)

    def AddStringField(self,layer,fieldname):
        #add field to layer
        layer.startEditing()
        layer.dataProvider().addAttributes([QgsField(fieldname, QVariant.String)])
        layer.updateFields()

#JoinPolilineToPoligon
    def Join(self,poliline,poligon):
        # Create new column for storing borderlines
        self.AddStringField(poligon,'lines')

        # Create a dictionary of all polygons
        feature_dict = {f['natcode']: f for f in poligon.getFeatures()}

        poligon.startEditing()
        #pair all lines with two poligon
        for line in poliline.getFeatures():
            line_id = str(line['id'])
            logging.info('Working on %s line',line_id)
            leftid = line['leftID']

            if leftid:
                f = feature_dict[leftid]
                if f['lines']:
                    str_ = str(f['lines']) + "," + line_id
                else:
                    str_ = line_id
                f['lines'] = str_
                poligon.updateFeature(f)


            rightid = line['rightID']
            if rightid:
                f = feature_dict[rightid]
                if f['lines']:
                    str_ = str(f['lines']) + "," + line_id
                else:
                    str_ = line_id
                f['lines'] = str_
                poligon.updateFeature(f)

        poligon.commitChanges()
