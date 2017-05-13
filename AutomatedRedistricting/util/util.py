import logging
from AutomatedRedistricting.mosa.objectives import ObjFunc

class Log():
    def __init__(self):
        self.objf = ObjFunc()

    def LogSolution(self,solution,info=None):
        if info:
            logging.info(info)

        logging.info("Solution objective values:%s",','.join(str(x) for x in solution.objective_values))

        try:
            logging.info("Weighted objective %f(%s)",solution.weighted_obj,'-'.join(str(x) for x in solution.weight_vectors))
        except AttributeError:
            logging.info("There are no weights")

    def LogObj(self,solution):
        self.objf.EvaluateObjectives(solution.counties,"log")
