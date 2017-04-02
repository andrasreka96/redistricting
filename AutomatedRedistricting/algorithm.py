import random
from util import *
import logging


class MOSA:

    TRY_FOR_FREE_NEIGHBOUR=30

    def __init__(self,layer_poligon,layer_poliline):
        #create util object with used layers
        self.util=Util(layer_poligon,layer_poliline)

    def FindNewStartPoint(self,neighbour_units,selectable_units):
        for unit in neighbour_units:
            #get neighbours of unit
            neighbours=set(self.util.getUnitsById(unit.neighbours))
            neighbours&=selectable_units
            #the new starting unit has been founded
            if neighbours:
                return neighbours.pop(),unit.district_id,1
        return None,None,-1

    def CreateInitialSolution(self,nr_of_districts):

        #get all units in the layer
        units = set(self.util.units)

        unit_in_district=len(units)/nr_of_districts
        solution=[]

        #get color for every district
        randomScheme = QgsRandomColorScheme()
        colors=randomScheme.fetchColors(nr_of_districts)

        potential_start_point=set()
        lastdistrict=None


        i=0;#number of created districts
        while units:
            logging.info('Bilding distirict %d has started',i+1)

            #start with a random unit from the set of unchosen units
            if solution:
                random_unit,lastdistrict,error = self.FindNewStartPoint(potential_start_point,units)
                if error == -1:
                    logging.info('Couldn\'t choose from border units')
                    random_unit=random.sample(units,1)[0]
            else:
                #choose a totally random unit
                random_unit=random.sample(units,1)[0]

            units.remove(random_unit)

            #the district is divided into two set
            district=set()

            #this set stores the units which hasn't been chosen before
            selectable_district=set([random_unit])

            j=0
            neighbour_units=set()
            #stop when enough units were found or there are no more free neighbour
            while j<=unit_in_district and selectable_district:

                #get a random unit from district
                    random_unit=random.sample(selectable_district,1)[0]

                    district.add(random_unit)
                    selectable_district.remove(random_unit)
                    #potential_start_point.remove(random_unit)

                    logging.info('Distirict %d:unit %s was added',i+1,random_unit.id)

                    neighbours_list=random_unit.neighbours

                    #find out which neighbour unit is free
                    neighbour_units=set(self.util.getUnitsById(neighbours_list))
                    neighbour_units&=units

                    new_neighbours_number=len(neighbour_units)
                    if new_neighbours_number:
                        #union
                        selectable_district |= neighbour_units

                        units -= neighbour_units

                        j+=new_neighbours_number
                        logging.info('%d unit has been added to district %d',new_neighbours_number,i+1)


            #units in new district
            new_district=district | selectable_district

            #extend the set of start points
            potential_start_point|=selectable_district

            #don't create new district if there are enough of it or it is too small
            if i>=nr_of_districts or len(new_district)<unit_in_district/4:
                #add units to an allready created district
                solution[lastdistrict].extand(new_district)
                logging.info('District %d:expanded by %d new units',lastdistrict,len(new_district))
            else:
                #create district and add to the solution

                solution.append(self.util.BuildDistrictFromUnits(i,new_district,colors[i]))
                logging.info('District %d has been added to the solution with %d units',i+1,len(new_district))
                #take the next district
                i+=1

        #make the final calculations for every district
        for s in solution:
            self.util.BuildDistrict(s)
        logging.info("Solution has been constructed")

        return solution


def updatePareto(U):
    if not dominate(U) and not dominated(U):
        addToPareto(U)
        assignWeight(U)
    else :
        if dominates(U):
            D = dominatedBy(U)
            C = random(D)
            C = U

def MOSA_(self):
#1,2
    weight_vectors = GenerateWeightVectors(number_of_nondominated_solutions)
    U = CreateInitialSolution()
    U.f = evaluate(U) # [C1(U),C2(U),..,Cn(U)]
    U.w = updatePareto(U)
    U.deltaf = dot(U.w,U.f)
#3-8
    while not frozen(T):
        V = randomPerturbation(U)
        V.f = evaluate(V)
        V.deltaf = dot(U.w,V.f)
        if ParetoUpdated:
            U=V
            w=updatePareto(V)
            #9??
            if added and len(pareto_set)>MAX:
                U=random.sample(pareto_set)

        else:
            if random.uniform(0, 1)<=probability(V.deltaf,T):
                U=V
        reduceTemperature(T)
