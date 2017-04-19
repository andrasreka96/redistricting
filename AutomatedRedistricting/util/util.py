from qgis.core import *
import logging

class QgsRandomColorScheme(QgsColorScheme):
    def __init__(self, parent=None):
        QgsColorScheme.__init__(self)

    def fetchColors(self, noColors):
        return [QColor.fromRgb(random.randrange(100,255),random.randrange(100,255),random.randrange(100,255)).name() for _ in range(noColors) ]

class Log():
    def LogSolution(self,counties,mosa):
        for county in counties:
            logging.info(county.toString())
            for district in county.districts:
                logging.info(district.toString())
        logging.info("Objective function of solution:%d",mosa.prob(counties))
