from AutomatedRedistricting.mosa.objectives import ObjFunc

class Solution:
    def __init__(self,counties,objective_values):
        self.counties = counties
        self.objective_values = objective_values
        self.district_dict = {d.unique_id:d for c in counties for d in c.districts}

    def changeDistrict(self,district):
        self.counties[district.county-1].districts[district.id] = district
        self.district_dict = {d.unique_id:d for c in self.counties for d in c.districts}
        self.objective_values =  ObjFunc().EvaluateObjectives(self.counties)
