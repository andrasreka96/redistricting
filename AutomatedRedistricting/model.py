class Unit:
    def __init__(self,id,name,population,neighbours,geoinf):
        #save the unit's name,
        self.id=id
        self.name=name
        #save the unit's population
        self.population=population
        #save the unit's neighbours
        self.neighbours=neighbours
        #save some geographical info
        self.geoinf=geoinf


    def show(self):
        print 'id:%s\nname:%s\npop:%s\nneighbours:%s' %(self.id,self.name,self.population,self.neighbours)

class District:
    def __init__(self,units,area,perimiter,population):
        self.units=units
        self.area=area
        self.perimiter=perimiter
        self.population=population
