import random
from util import *
import logging

class InitialSolution:

    ATTRIBUTE_NAME='name'
    ATTRIBUTE_POPULATION='pop2015'
    ATTRIBUTE_ID='natcode'
    ATTRIBUTE_NEIGHBOURS='neighbours'

    TRY_FOR_FREE_NEIGHBOUR=15

    logging.basicConfig(format='%(asctime)s %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p',
                filename='/home/reka/Documents/redistricting/AutomatedRedistricting/log/logs.log',
                filemode='w',
                level=logging.INFO)

    def CreateInitialSolution(self,nr_of_districts,layer):
        util=Util(layer)
        units = util.getUnits(layer.getFeatures(),self.ATTRIBUTE_ID,self.ATTRIBUTE_NAME,self.ATTRIBUTE_POPULATION,self.ATTRIBUTE_NEIGHBOURS)

        unit_in_district=len(units)/nr_of_districts
        solution=[]

        #get color for every district
        randomScheme = QgsRandomColorScheme()
        colors=randomScheme.fetchColors(30)

        for i in range(nr_of_districts):
            logging.info('Bilding distirict %d has started,color:%s',i+1,colors[i])

            #start with a random unit from the set of unchosen units
            random_unit = random.choice(units)
            units.remove(random_unit)
            selectable_units=set(units)

            #start point of district
            district=set([random_unit])
            j=0
            noneighbourfound=0
            #stop when enough units were found or there are no more neighbour unit
            while j<=unit_in_district and noneighbourfound<self.TRY_FOR_FREE_NEIGHBOUR:
                #get a random unit from district
                random_unit=random.sample(district,1)[0]
                logging.info('Distirict %d:unit %s was added',i+1,random_unit.getID())


                neighbours_list=random_unit.getNeighbours()

                #find out which neighbour unit is free
                neighbour_units=set(util.getUnitsById(neighbours_list,units))
                neighbour_units&=selectable_units

                #logger.info("Neighbours:")
                #for unit in neighbour_units:
                #    logging.info("neighbour %s founded",unit.getID())

                new_neighbours_number=len(neighbour_units)
                if new_neighbours_number:
                    #union
                    district |= neighbour_units

                    selectable_units -= neighbour_units

                    j+=new_neighbours_number
                    noneighbourfound=0;
                    logging.info('%d unit has been added to district %d',new_neighbours_number,i+1)
                else:
                    logging.info('District %d:No neighbour found %d',i+1,noneighbourfound)
                    noneighbourfound+=1


            #add the new district to the solution
            solution.append(util.BuildDistrictFromUnits(i,district,colors[i]))
            logging.info('district %d has been added to the solution',i+1)

            #brrrrrrr
            units=list(selectable_units)

        return solution

class SA:
    def __init__ (temperature,f,alpha,initial_plan):
        self.temperature=temperature
        self.f=f
        self.alpha=alpha
        self.initial_plan=initial_plan
