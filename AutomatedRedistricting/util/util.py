from qgis.core import *
from PyQt4.QtGui import QColor
import logging,random

class QgsRandomColorScheme(QgsColorScheme):
    def __init__(self, parent=None):
        QgsColorScheme.__init__(self)

    def fetchColors(self, noColors):
        return [QColor.fromRgb(random.randrange(100,255),random.randrange(100,255),random.randrange(100,255)).name() for _ in range(noColors) ]

class Log():
    def LogSolution(self,solution):
        logging.info("Solution objective values:%s",','.join(str(x) for x in solution.objective_values))
        for county in solution.counties:
            logging.info(county.toString())
            for district in county.districts:
                logging.info(district.toString())

    def LogObjectives(self,solution):
        logging.info("Solution objective values:%s",','.join(str(x) for x in solution.objective_values))
