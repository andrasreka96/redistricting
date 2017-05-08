class Unit:

    def __init__(self,id,name,population,neighbours,lines,area):
        #save the unit's name,
        self.id=id
        self.name=name
        #save the unit's population
        self.population=population
        #save the unit's neighbours
        self.neighbours=neighbours
        self.lines=set(lines.split(','))
        #save area
        self.area=area

    def toString(self):
        return "id:%s\nname:%s\npop:%s\n" % (self.id,self.name,self.population)
