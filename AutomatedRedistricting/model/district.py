import logging
class District:
    def __init__(self,id,unique_id,units,color,area=None,perimeter=None,population=None,borders=None):
        self.id=id
        self.unique_id=unique_id
        self.color=color
        self.units=units
        self.area=area
        self.perimeter=perimeter
        self.population=population

        if borders:
            self.borders=borders
        else:
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
            neighbours = unit.neighbours
            #find units which have neighbours out of district
            if neighbours - self.units:
                self.borders.add(unit)
