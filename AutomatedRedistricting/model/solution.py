from AutomatedRedistricting.mosa.objectives import ObjFunc

class Solution:
    def __init__(self,counties,objective_values,temperature=0,iter=0):
        self.iter = iter
        self.temperature = temperature
        self.counties = counties
        self.objective_values = objective_values

    def weights(self,weights):
        self.weight_vectors = weights
        self.weighted_obj = sum([a*b for a,b in zip(self.objective_values,weights)])
