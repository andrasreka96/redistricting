from qgis.core import *
from PyQt4.QtGui import QColor
import logging,random
from AutomatedRedistricting.mosa.objectives import ObjFunc


class QgsRandomColorScheme(QgsColorScheme):
    def __init__(self, parent=None):
        QgsColorScheme.__init__(self)

    def fetchColors(self, noColors):
        return [QColor.fromRgb(random.randrange(100,255),random.randrange(100,255),random.randrange(100,255)).name() for _ in range(noColors) ]

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
