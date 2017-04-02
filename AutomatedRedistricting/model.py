class Unit:
    def __init__(self,feature,id,name,population,neighbours,lines,geoinf):
        #save the unit's name,
        self.feature=feature
        self.id=id
        self.name=name
        #save the unit's population
        self.population=population
        #save the unit's neighbours
        self.neighbours=set(neighbours.split(','))
        self.lines=set(lines.split(','))
        #save some geographical info
        self.area=geoinf.area()
        self.geoinf=geoinf
        self.district_id=None

    def show(self):
        print 'id:%s\nname:%s\npop:%s\nneighbours:%s' %(self.id,self.name,self.population,self.neighbours)

class District:
    def __init__(self,id,units,color,area=0,perimiter=0,population=0):
        self.id=id
        self.color=color
        self.units=units
        self.area=area
        self.perimiter=perimiter
        self.population=population

    def show(self):
        for unit in self.units:
            unit.show()

    def extand(self,units):
        self.units=set(self.units)|units
