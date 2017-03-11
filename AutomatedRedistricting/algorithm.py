import random
import logging
from util import *

class InitialSolution:

    logging.basicConfig(format='%(asctime)s %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p',
                filename='/home/reka/Documents/redistricting/AutomatedRedistricting/log/InitialSolution.log',
                filemode='w',
                level=logging.INFO)

    ATTRIBUTE_NAME='name'
    ATTRIBUTE_POPULATION='pop2015'
    ATTRIBUTE_ID='natcode'
    ATTRIBUTE_NEIGHBOURS='neighbours'

    def CreateInitialSolution(self,nr_of_districts,layer):
        util=Util(layer)
        units = util.getUnits(layer.getFeatures(),self.ATTRIBUTE_ID,self.ATTRIBUTE_NAME,self.ATTRIBUTE_POPULATION,self.ATTRIBUTE_NEIGHBOURS)

        unit_in_district=len(units)/nr_of_districts
        solution=[]
        units_set=set(units)

        randomScheme = QgsRandomColorScheme()
        colors=randomScheme.fetchColors(30,QColor(100))

        for i in range(nr_of_districts-1):
            logging.info('Bilding distirict %d has started',i+1)
            units_in_district=set()
            unit=units.pop(random.randrange(len(units)))

            j=0
            while j<unit_in_district:

                #first unit
                if units_in_district:
                    unit=units_in_district.pop()

                units_in_district.add(unit)
                logging.info('Unit %s was randomly chosen',unit.getID())

                neighbours_list=unit.getNeighbours()
                j+=len(neighbours_list)+1
                neighbour_units=set(util.getUnitsById(neighbours_list,units_set))
                units_in_district |= neighbour_units

                logging.info('%d unit has been added to district %d',len(neighbours_list),i)

                units_set -= neighbour_units
            #add the new district to the solution
            solution.append(util.BuildDistrictFromUnits(i,units_in_district,colors[i]))
            logging.info('district %d has been added to the solution',i)

        return solution

class SA:
    def __init__ (temperature,f,alpha,initial_plan):
        self.temperature=temperature
        self.f=f
        self.alpha=alpha
        self.initial_plan=initial_plan
