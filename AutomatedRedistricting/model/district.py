class District:
    def __init__(self,id,units,color,area=0,perimiter=0,population=0):
        self.id=id
        self.color=color
        self.units=units
        self.area=area
        self.perimiter=perimiter
        self.population=population
        self.setBorders()

    def show(self):
        for unit in self.units:
            unit.show()

    def showBorders(self):
        for u in self.borders:
            u.show()

    def extand(self,units):
        self.units=set(self.units)|units
        self.setBorders()

    def setBorders(self):
        borders = set()
        for u1 in self.units:
            neighbours=u1.neighbours
            for u2 in self.units:
                if u1 != u2:
                    neighbours|=u2.neighbours
            if neighbours:
                borders.add(u1)

        self.borders=borders
