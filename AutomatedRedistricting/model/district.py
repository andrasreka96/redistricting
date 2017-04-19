import logging
class District:
    def __init__(self,id,units,color,county,area=0,peremiter=0,population=0):
        self.id=id
        self.unique_id=str(county)+'_'+str(id)
        self.color=color
        self.units=units
        self.setUnitIds(units)
        self.unitids = set([unit.id for unit in units])
        self.area=area
        self.perimeter=peremiter
        self.population=population
        self.county=county
        self.setBorders()

    def toString(self):
        return "District %s:\ncolor:%s\narea:%d\nperimeter:%d\npopulation:%d" % (self.unique_id,self.color,self.area,self.perimeter,self.population)

    def showBorders(self):
        for u in self.borders:
            u.show()

    def setUnitIds(self,units):
        for u in units:
            u.district_id = self.unique_id
            u.color=self.color

    def extand(self,units):
        self.units=set(self.units)|units
        self.unitids=set(self.unitids)|set([unit.id for unit in units])
        self.setUnitIds(units)
        self.setBorders()

    def remove(self,units):
        self.units=set(self.units)-units
        self.unitids=set(self.unitids)-set([unit.id for unit in units])
        self.setBorders()

    def setBorders(self):
        borders = set()
        borderids = set()

        for unit in self.units:
            # set of neighbourhood units
            neighbourids = unit.neighbours
            neighbourids.add(unit.id)

            if len(self.unitids & neighbourids) != len(neighbourids):
                borders.add(unit)
                borderids.add(unit.id)

        self.borders=borders
        self.borderids=borderids
