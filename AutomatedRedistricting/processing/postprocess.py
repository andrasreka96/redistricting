from AutomatedRedistricting.layer_manipulation import layer
from AutomatedRedistricting.util import util
import random

def showResults(layer_painter,solutions,patch):


    minims = random.sample(solutions,1)[0]
    minimv = sum(minims.objective_values)
    for s in solutions:
        util.logSolution(s)
        if minimv>sum(s.objective_values):
            minims = s

    util.logSolution(minims,"Best Solution")
    layer_painter.colorSolution(minims,'color1')

    util.logSolution(patch,"Patch Solution")
    layer_painter.colorSolution(patch,'color2')
