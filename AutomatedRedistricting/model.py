class Unit:
    def __init__(self,feature,id,name,population,neighbours,geoinf):
        #save the unit's name,
        self.feature=feature
        self.id=id
        self.name=name
        #save the unit's population
        self.population=population
        #save the unit's neighbours
        self.neighbours=neighbours.split(',')
        #save some geographical info
        self.geoinf=geoinf


    def show(self):
        print 'id:%s\nname:%s\npop:%s\nneighbours:%s' %(self.id,self.name,self.population,self.neighbours)

    def getID(self):
        return self.id

    def getFeature(self):
        return self.feature

    def getNeighbours(self):
        return self.neighbours

    def getNumberOfNeighbours(self):
        return len(self.neighbours)

    def getArea(self):
        return self.geoinf.area()

    def getPopulation(self):
        return self.getPopulation()

class District:
    def __init__(self,id,color,units,area,perimiter,population):
        self.id=id
        self.color=color
        self.units=units
        self.area=area
        self.perimiter=perimiter
        self.population=population

    def show(self):
        for unit in units:
            unit.show()
