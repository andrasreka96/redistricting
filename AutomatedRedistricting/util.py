from qgis.core import QgsGeometry
from model import Unit

class Query:
    def where(self,exp):
        exp=QgsExpression(exp)
        if exp.hasParserError()==0:
            exp.prepare(self.layer.pendingFields())
            for feature in self.layer.getFeatures():
                value = exp.evaluate(feature)
                if bool(value):
                    yield feature

class UnitBilder:
    def getUnits(self,features,attribute_id,attribute_name,attribute_population,attribute_neighbours):
        return  [Unit(feature[attribute_id],feature[attribute_name],feature[attribute_population],feature[attribute_neighbours],feature.geometry()) for feature in features]

class DistrictBilder:
    def getPerimiter(self,units):
        #it makes one polygon from units then returns its perimiter
        geoms = QgsGeometry.fromWkt('GEOMETRYCOLLECTION EMPTY')
        for unit in units:
            geoms = geoms.combine(unit.geometry())
        print geoms.geometry.perimiter()
