import random
from util import *
import logging
from collections import defaultdict
import yaml
import os.path

from AutomatedRedistricting.model.county import County

class MOSA:

    def __init__(self,layer_poligon,layer_poliline,layer_county):
        #load yaml
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)

        self.attributes = data.get('attributes')
        self.parameters = data.get('parameters')
        #create util object with used layers
        self.layer_poligon=layer_poligon

        #create dictionarie where
        #key - countyid
        #values - lists of features
        dictionarie = defaultdict(list)
        for feature in layer_poligon.getFeatures():
            dictionarie[feature[self.attributes['county_id']]].append(feature)
        self.dictionarie=dictionarie

        self.layer_poliline=layer_poliline
        self.layer_county=layer_county
        self.counties_dict = {f[self.attributes['county_id']] : f[self.attributes['county_name']] for f in layer_county.getFeatures()}


    def DistrictNear(self,units,util,solution):
        for i in units:
            unit = set(util.getUnitsById(i.neighbours))
            for district in solution:
                if unit & district.borders:
                    return district.id

    def CreateInitialSolution(self,nr_of_districts,units):
        #convert features into unit objects
        util = Util(units,self.layer_poligon,self.layer_poliline)
        units = set(util.units)

        unit_in_district=len(units)/nr_of_districts
        solution=[]

        #get color for every district
        randomScheme = QgsRandomColorScheme()
        colors=randomScheme.fetchColors(nr_of_districts)

        i=0;#number of created districts
        while units:
            logging.info('Bilding distirict %d has started',i+1)

            random_unit=random.sample(units,1)[0]
            units.remove(random_unit)
            #the district is divided into two set
            district=set()
            #this set stores the units which hasn't been chosen before
            #random_unit will be chosen firstly
            selectable_district=set([random_unit])

            j=0
            neighbour_units=set()
            #stop when enough units were found or there are no more free neighbour
            while j<=unit_in_district and selectable_district:

                #get a random unit from district
                    random_unit=random.sample(selectable_district,1)[0]

                    district.add(random_unit)
                    selectable_district.remove(random_unit)

                    #list of neighbours
                    neighbours_list=random_unit.neighbours

                    #find out which neighbour unit is free
                    neighbour_units=set(util.getUnitsById(neighbours_list))
                    neighbour_units&=units

                    new_neighbours_number=len(neighbour_units)
                    if new_neighbours_number:
                        selectable_district |= neighbour_units
                        units -= neighbour_units
                        j+=new_neighbours_number
                        logging.info('%d units has been added to district %d',new_neighbours_number+1,i+1)

            #units in new district
            new_district=district | selectable_district

            #don't create new district if there are enough of it or it is too small
            if i>=nr_of_districts or len(new_district)<unit_in_district/4:
                #add units to an allready created district
                ind=self.DistrictNear(new_district,util,solution)
                solution[ind].extand(new_district)
                logging.info('District %d:expanded by %d new units',ind,len(new_district))
            else:
            #create district and add to the solution
                solution.append(util.BuildDistrictFromUnits(i,new_district,colors[i]))
                logging.info('District %d has been added to the solution with %d units',i+1,len(new_district))
                #take the next district
                i+=1

        #make the final calculations for every district
        for s in solution:
            util.BuildDistrict(s)

        return solution

    def CreateInitialDistricts(self):
        #create districts for every county
        counties = []
        for countyid in range(1,self.parameters['num_of_counties'] + 1):
            #get units in county
            units = self.dictionarie[countyid]
            logging.info("Working on county %d(%d units)",countyid,len(units))
            districts = self.CreateInitialSolution(self.parameters['nr_of_districts'],units)
            counties.append(County(countyid,self.counties_dict[countyid],districts))
        return counties

    def updatePareto(U):
        if not dominate(U) and not dominated(U):
            addToPareto(U)
            assignWeight(U)
        else :
            if dominates(U):
                D = dominatedBy(U)
                C = random(D)
                C = U

    def dot(x,y):
        return sum([a*b for a,b in zip(x,y)])

    def MOSA_(self):
    #1,2
        weight_vectors = GenerateWeightVectors(number_of_nondominated_solutions)
        U.s = CreateInitialSolution()
        U.f = evaluate(U) # [C1(U),C2(U),..,Cn(U)]
        U.w = updatePareto(U)
        U.deltaf = dot(U.w,U.f)
    #3-8
        while not frozen(T):
            V.s = randomPerturbation(U)
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
