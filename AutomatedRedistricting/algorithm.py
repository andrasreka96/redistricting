class InitialPlan:
    def CreateInitialPlan(nr_of_districts,units):
        districts=[]
        units_set=Set(units)
        unit_in_district=len(units)/nr_of_districts
        for i in range(nr_of_districts-1):
            district=[]
            j=0
            while j<unit_in_district:
                unit=units.pop()
                district.append(unit)
                neighbors=unit.neighbors(units)
                district.append(neighbors)
                j+=len(neighbors)
                units.pop(neighbors)



class SA:
    def __init__ (temperature,f,alpha,initial_plan):
        self.temperature=temperature
        self.f=f
        self.alpha=alpha
        self.initial_plan=initial_plan
