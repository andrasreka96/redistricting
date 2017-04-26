import logging
class District:
    def __init__(self,id,unique_id,units,color,area=0,peremiter=0,population=0):
        self.id=id
        self.unique_id=unique_id
        self.color=color
        self.units=units
        self.area=area
        self.perimeter=peremiter
        self.population=population
        self.setBorders()

    def toString(self):
        return "District %s:\ncolor:%s\narea:%d\nperimeter:%d\npopulation:%d\n%s\n%s" % (self.unique_id,self.color,self.area,self.perimeter,self.population,[u.toString() for u in self.units],[u.toString() for u in self.borders])

    def extand(self,units):
        self.units=set(self.units)|units
        self.setBorders()

    def remove(self,units):
        self.units=set(self.units)-units
        self.setBorders()

    def setBorders(self):
        self.borders = set()
        for unit in self.units:
            # set of neighbourhood units
            neighbours = unit.neighbours
            #find units which have neighbours out of district
            if neighbours - self.units:
                self.borders.add(unit)
