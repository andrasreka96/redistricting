class County:
    def __init__(self,id,name,districts,population=None):
        self.id=id
        self.name=name
        self.districts=districts
        self.population = sum([district.population for district in districts])

    def toString(self):
        return "County %s(%d) with %d districts and %d population" % (self.name,self.id,len(self.districts),self.population)
