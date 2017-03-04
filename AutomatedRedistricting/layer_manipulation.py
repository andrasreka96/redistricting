from qgis.core import QgsField
from PyQt4.QtCore import QVariant

class FieldControl:

    def AddStringField(self,layer,fieldname):
        #add field to layer
        layer.startEditing()
        layer.dataProvider().addAttributes([QgsField(fieldname, QVariant.String)])
        layer.updateFields()
