import logging
from AutomatedRedistricting.mosa.objectives import ObjFunc
import math
from itertools import islice
from PyQt4.QtGui import QColor


class Log():
    def __init__(self,objf):
        self.objf = objf

    def LogSolution(self,solution,info=None):
        if info:
            logging.info(info)

        logging.info("Solution was found at temperature %f,iteration %d",solution.temperature,solution.iter)
        logging.info("With objective values:%s",','.join(str(x) for x in solution.objective_values))

        try:
            logging.info("Weighted objective %f(%s)",solution.weighted_obj,'-'.join(str(x) for x in solution.weight_vectors))
        except AttributeError:
            logging.info("There are no weights")

    def LogObj(self,solution):
        self.objf.EvaluateObjectives(solution.counties,"log")

class Color():

    def iteratef(self,f,x,n):
            if n == 0:
                return []
            else:
                return [f(x)] + self.iteratef(f,f(x),n-1)

    def allVariatons(self,values,length,ind,newlist):

        if ind == length:
            yield newlist[:]
        else:
            for i in values:
                newlist[ind]=i
                for result in self.allVariatons(values,length,ind+1,newlist):
                    yield result


    def generateColors(self,n):
        basecolors_number = math.ceil(math.pow(n+2,1.0/3.0))
        basecolors =self.iteratef(lambda x:x+20,0,basecolors_number)
        basecolors.append(0)

        colors = [QColor(color[0],color[1],color[2]) for color in self.allVariatons(basecolors,3,0,[0,0,0])]

        return colors[1:len(colors)-2]

    def lighter(self,color,n,value):

        colors = [color]
        for _ in range(0,n):
            color = color.lighter(100+value)
            colors.append(color)

        return colors

    def RGBtoHex(self,colors):
        return [[color.name() for color in c] for c in colors]
