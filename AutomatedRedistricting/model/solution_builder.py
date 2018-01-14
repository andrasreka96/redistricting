from AutomatedRedistricting.model.county import County
from AutomatedRedistricting.model.solution import Solution
from AutomatedRedistricting.model.district import District

class SolutionBuilder:

    def CopyCounty(self,county):
    #create district objects with same attribute values
        districts = [District(d.id,d.unique_id,d.units,d.color,d.area,d.perimeter,d.population,d.borders) for d in county.districts]

        # keep the other attributes as it were
        return County(county.id,county.name,districts,county.deviation,county.population)

    def CopySolution(self,solution):
        counties = [self.CopyCounty(county) for county in solution.counties]
        return Solution(counties,list(solution.objective_values))
