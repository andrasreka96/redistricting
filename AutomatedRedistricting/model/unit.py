
import logging
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
        self.color=None

    def toString(self):
        return 'id:%s\nname:%s\npop:%s\nneighbours:%s' % (self.id,self.name,self.population,self.neighbours)
