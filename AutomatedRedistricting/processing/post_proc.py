import random
from AutomatedRedistricting.model.solution import Solution

class PostProcessing:
    def __init__(self,solutions,objf,log):
        self.solutions = solutions
        self.objf = objf
        self.log = log

    def dot(self,x,y):
        d= sum([a*b for a,b in zip(x,y)])
        return d

    def patchSolution(self,w):
    #it splits the solutions, selects between them, than creates the best solution from the pieces
        counties = []
        for i in range(0,len(random.sample(self.solutions,1)[0].counties)):
            bestcounty = next(iter(self.solutions)).counties[i]
            #determine the objectibe value for the given weights
            bestval = self.dot(self.objf.EvaluateObjectives([bestcounty]),w)

            #look for the best redistricting plan of the county
            for s in self.solutions:
                val = self.dot(self.objf.EvaluateObjectives([s.counties[i]]),w)
                if bestval > val:
                    bestcounty = s.counties[i]
                    bestval = val
            counties.append(bestcounty)

        return Solution(counties,self.objf.EvaluateObjectives(counties))

    def showResults(self,layer_manipulation,w):
        minims = random.sample(self.solutions,1)[0]
        minimff = minims
        min_weighted_obj = self.dot(minimff.objective_values,minimff.weight_vectors)
        for s in self.solutions:
            self.log.LogSolution(s)
            if minims.weighted_obj>s.weighted_obj:
                minims = s
            if s.weight_vectors[0] == s.weight_vectors[1] and min_weighted_obj>s.weighted_obj:
                minimff = s
                min_weighted_obj = s.weighted_obj

        self.log.LogSolution(minims,"Best Solution")
        layer_manipulation.ColorDistricts(minims.counties,'color1')
        self.log.LogObj(minims)

        self.log.LogSolution(minimff,"Best Solution(5-5)")
        layer_manipulation.ColorDistricts(minimff.counties,'color2')
        self.log.LogObj(minimff)

        for i in range(0,len(w)):

            patch = self.patchSolution(w[i])
            self.log.LogSolution(patch,"Patch Solution " + ', '.join(str(x) for x in w[i]))
            layer_manipulation.ColorDistricts(minimff.counties,'color' + str(i+3))
            self.log.LogObj(minimff)
