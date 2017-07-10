from __future__ import division
from collections import deque
from itertools import islice

import random
import logging
from collections import defaultdict
import yaml
import os.path
import math


from AutomatedRedistricting.model.county import County
from AutomatedRedistricting.model.solution import Solution
from AutomatedRedistricting.model.district import District
from AutomatedRedistricting.model.dis_build import DistrictBuilder
from AutomatedRedistricting.model.sol_build import SolutionBuilder
from AutomatedRedistricting.model.unit_build import UnitBuilder
from AutomatedRedistricting.layer_manipulation.layer import LayerManipulation
from AutomatedRedistricting.util.util import *

import objectives

from PyQt4.QtGui import QColor

class MOSA:

    def __init__(self,layer_poligon,layer_poliline ):
        #load yaml
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)

        attributes = data.get('attributes')
        parameters = data.get('parameters')

        #save used layers
        self.layer_poligon=layer_poligon

        #create dictionary where
        #key - regionid
        #values - lists of features
        self.dict_units = defaultdict(list)

        self.attrib_join_id = attributes['join_id']
        self.attrib_pop = attributes['attribute_population']

        self.cooling_schedule = parameters['cooling_schedule']
        self.initial_temperature = parameters['initial_temperature']
        self.final_temperature = parameters['final_temperature']
        self.iterations = parameters['iterations']
        self.small_partition = parameters['small_partition']
        self.upper_limit = parameters['upper_limit']
        self.neighbourhood = parameters['neighbourhood']
        self.weight_vectors = parameters['weight_vectors']
        self.minnr_of_unit = parameters['minnr_of_unit']
        self.max_iter = parameters['max_iter']
        self.max_size_pareto = parameters['max_size_pareto']
        self.nr_of_districts = parameters['nr_of_districts']

        self.district_builder = DistrictBuilder(layer_poliline,attributes['attribute_id_poliline'])

        self.attributes=attributes


    def BuildRegion(self):
        idx = self.layer_poligon.fieldNameIndex(self.attrib_join_id)
        uniqueValues = self.layer_poligon.uniqueValues(idx)

        self.nr_of_regions = len(uniqueValues)
        self.dict_pop = dict.fromkeys(uniqueValues,0)
        self.population_country = 0

        for feature in self.layer_poligon.getFeatures():
            self.population_country +=  feature[self.attrib_pop]
            self.dict_pop[feature[self.attrib_join_id]] += feature[self.attrib_pop]
            self.dict_units[feature[self.attrib_join_id]].append(feature)

        #init population related stuff
        self.national_mean = self.population_country/self.nr_of_districts
        self.objf = objectives.ObjFunc(self.national_mean)
        self.log = Log(self.objf)

    def DistrictNear(self,units,solution):
        for unit in units:
            for district in solution:
                if (unit.neighbours & district.borders):
                    return district.id

    def RandomChoise(self,setfrom,setinto):
        random_unit=random.sample(setfrom,1)[0]
        setfrom.remove(random_unit)
        setinto.add(random_unit)
        return random_unit

    def CreateInitialCounty(self,nr_of_districts,features,county):

        #convert features into unit objects
        util = UnitBuilder(features,self.attributes)
        units = set(util.units)

        unit_in_district=len(units)/nr_of_districts
        solution=[]

        i=0
        while units:

            #the district is divided into two set
            district=set()

            #this set stores the units which hasn't been chosen before
            selectable_district=set()

            #select the first unit randomly
            self.RandomChoise(units,selectable_district)

            j=0

            #search until enough units were found or there are no more free neighbour
            while j<=unit_in_district-self.upper_limit and selectable_district:

            	#start with a random unit from district
                random_unit = self.RandomChoise(selectable_district,district)

                #find out which neighbour units are free
                neighbour_units=random_unit.neighbours&units

                new_neighbours_number=len(neighbour_units)
                if new_neighbours_number:
                    selectable_district |= neighbour_units
                    units -= neighbour_units
                    j += new_neighbours_number
                    logging.debug('%d units has been added to district %d',new_neighbours_number+1,i+1)

            #units in new district
            new_district=district | selectable_district

            #don't create new district if there are enough of it or it wwould be too small
            if i>=nr_of_districts or len(new_district)<unit_in_district/self.small_partition:
            #add units to an already existing district

                ind=self.DistrictNear(new_district,solution)
                if ind is not None:
                    solution[ind].extand(new_district)
                    logging.debug('District %d:expanded by %d new units',ind,len(new_district))
                else:
                    #rare case of small,segregated units
                    logging.info("Index exception")
                    units|=new_district
            else:
            #create district and add to the solution

                solution.append(District(i,str(county)+'_'+str(i),new_district,self.colors[i]))
                logging.debug('District %d has been added to the solution with %d units',i+1,len(new_district))

                #take the next district
                i+=1

        #make the final calculations for every district
        for s in solution:
            self.district_builder.BuildDistrict(s)
        return solution

    def AssignDistricts(self):

        dict_assigned = {i: (self.dict_pop[i]//self.national_mean,self.dict_pop[i]/self.national_mean - self.dict_pop[i]//self.national_mean) for i in range(1,self.nr_of_regions + 1)}

        assigned = 0
        for key, value in dict_assigned.iteritems():
            if value[0] == 1:
                dict_assigned[key] = (2,0)
                assigned+=2
            else:
                assigned+=value[0]

        #romania specific
        #assigned-=(dict_assigned[40][0]-6)
        #dict_assigned[40]=(6,0)


        unassigned = self.nr_of_districts-assigned
        #assigne an additional district to counties with the highest fractional remainder
        if unassigned:
            dict_sorted = sorted(dict_assigned.items(), key=lambda (k, v): v[1],reverse=True)
            for key,value in list(islice(dict_sorted, unassigned)):
                dict_assigned[key] = (value[0]+1,value[1])


        assigned_districts = [assv for (assv,rem) in dict_assigned.values()]
        logging.info("Assigned Districts:%s", ','.join(str(x) for x in assigned_districts))
        #return the assigned values
        return assigned_districts

    def CreateInitialSolution(self):
    #create districts for every region
        self.BuildRegion()

        counties = []
        district_in_counties = self.AssignDistricts()
        self.colors =  Color().generateColors(max(district_in_counties))
        for countyid in range(1,self.nr_of_regions + 1):
            #get units in county
            units = self.dict_units[countyid]

            district = self.CreateInitialCounty(district_in_counties[countyid-1],units,countyid)

            #determine the allowed deviations in each county

            #differene between the national and state mean
            diff = abs(self.dict_pop[countyid]/district_in_counties[countyid-1]-self.national_mean)

            #store deviations in county
            if diff<self.dict_pop[countyid]*(5/100):
                deviation = 15
            else:
                if diff < self.dict_pop[countyid]/10:
                    deviation = 10
                else:
                    deviation = 5

            county = County(countyid,countyid,district,deviation)
            counties.append(county)



        objectives = self.objf.EvaluateObjectives(counties)
        LayerManipulation(self.layer_poligon).ColorDistricts(counties,'color')

        solution = Solution(counties,objectives)
        self.log.LogSolution(solution,"Initial Solution")
        self.log.LogObj(solution)
        return solution

    def BFS(self,district):
    #Decide if the given district is connected

        units = district.borders
        visited = set()
        q = deque()
        root = random.sample(units,1)[0]
        q.append(root)
        visited.add(root)

        while q:
            current = q.popleft()
            for unit in (current.neighbours & units):
                if unit not in visited:
                    visited.add(unit)
                    q.append(unit)

        if units-visited:
            return False
        return True

    def randomChaine(self,units,length):
        unit = random.sample(units,1)[0]
        units.remove(unit)
        chaine = set([unit])

        iteration = 0
        while len(chaine)<length and units and iteration<self.max_iter:

            neighbours = set()
            for unit in units:
                if unit.neighbours & chaine:
                    neighbours.add(unit)
            chaine|=neighbours
            units-=neighbours
            iteration+=1

        return chaine

    def MoveUnits(self,solution,change):

        #random county where the changes will be made
        county  = random.choice(solution.counties)

    	units_to_move=set()

        while not units_to_move:
        #move units from d1 to d2
            (d1,d2) = random.sample(county.districts,2)
            for unit in d2.borders:
                units_to_move |= unit.neighbours & d1.borders

        #don't move more units than it's necessary
        if change!=-1 and len(units_to_move)-change>0:
            units_to_move = self.randomChaine(units_to_move,change)

        #can't leave a district empty
        if len(d1.units-units_to_move) > self.minnr_of_unit:
            if self.BFS(District(1,'',d1.units-units_to_move,'')):

                d2.extand(units_to_move)
                d1.remove(units_to_move)

                self.district_builder.BuildDistrict(d1)
                self.district_builder.BuildDistrict(d2)


    def NeighbourSolution(self,solution):
        new_solution = SolutionBuilder().CopySolution(solution)
        for depth in self.neighbourhood:
            self.MoveUnits(new_solution,depth)

        #update objective values according to new solution
        new_solution.objective_values = self.objf.EvaluateObjectives(new_solution.counties)
        return new_solution

    def dot(self,x,y):
        d= sum([a*b for a,b in zip(x,y)])
        return d

    def frozen(self,t):
        return t<=self.final_temperature

    def reduceTemperature(self,t):
        return t*self.cooling_schedule

    def ObjectivesSum(self,counties,weights):
        #returns the scalar product of the objective functions and their weights
        return self.dot(self.objf.EvaluateObjectives(counties),weights)

    def Dominations(self,new_solution,pareto):
        dominated = False
        dominate = []
        for solution in pareto:
            dominatedbys = True
            dominatess = True
            for new,old in zip(new_solution.objective_values, solution.objective_values):
                dominatedbys = dominatedbys and old<new
                dominatess = dominatess and new<old

            dominated = dominated or dominatedbys
            if dominatess:
                dominate.append(solution)

        return (dominated,dominate)

    def ChooseBetweenDominated(self,solution,dominates):
        best = dominates.pop()

        #how much better is the solution than the dominated one
        distance = best.weighted_obj - self.dot(solution.objective_values,best.weight_vectors)

        for s in dominates:
            hip_distance =  s.weighted_obj - self.dot(solution.objective_values,s.weight_vectors)
            if hip_distance>distance:
                distance = hip_distance
                best = s
        return best

    def UpdatePareto(self,solution,pareto):
        (dominated,dominates) = self.Dominations(solution,pareto)

        if not dominated and not dominates:
        	#set weights
            solution.weight_vectors = random.sample(self.weight_vectors,1)[0]

            #set weighted objective function
            solution.weighted_obj = self.dot(solution.weight_vectors,solution.objective_values)
            return 1

        if dominates:

            removable_solution = self.ChooseBetweenDominated(solution,dominates)
            solution.weight_vectors = removable_solution.weight_vectors
            solution.weighted_obj = self.dot(solution.weight_vectors,solution.objective_values)
            removable_solution = solution
            self.log.LogSolution(removable_solution,"New solution")
            return 2

        return 0

    def probability(self,obj1,obj2,t):
        diff=obj1-obj2
        if diff>=0:
            return 1
        try:
            ans = math.exp(diff/t)
        except OverflowError:
            ans = 0

        return ans

    def patchSolution(self,pareto,w):
    #it splits the solutions, selects between them, than creates the best solution from the pieces
        counties = []

        for i in range(0,self.nr_of_regions):
            bestcounty = next(iter(pareto)).counties[i]
            #determine the objectibe value for the given weights
            bestval = self.dot(self.objf.EvaluateObjectives([bestcounty]),w)

            #look for the best redistricting plan of the county
            for s in pareto:
                val = self.dot(self.objf.EvaluateObjectives([s.counties[i]]),w)
                if bestval > val:
                    bestcounty = s.counties[i]
                    bestval = val
            counties.append(bestcounty)

        return Solution(counties,self.objf.EvaluateObjectives(counties))

    def showResults(self,pareto):
        minims = random.sample(pareto,1)[0]
        minimff = minims
        min_weighted_obj = self.dot(minimff.objective_values,minimff.weight_vectors)
        for s in pareto:
            self.log.LogSolution(s)
            if minims.weighted_obj>s.weighted_obj:
                minims = s
            if s.weight_vectors[0] == s.weight_vectors[1] and min_weighted_obj>s.weighted_obj:
                minimff = s
                min_weighted_obj = s.weighted_obj

        self.log.LogSolution(minims,"Best Solution")
        LayerManipulation(self.layer_poligon).ColorDistricts(minims.counties,'color1')
        self.log.LogObj(minims)

        self.log.LogSolution(minimff,"Best Solution(5-5)")
        LayerManipulation(self.layer_poligon).ColorDistricts(minimff.counties,'color2')
        self.log.LogObj(minimff)

        self.log.LogSolution(self.patchSolution(pareto,[0.5,0.5]),"Patch Solution(5-5)")
        LayerManipulation(self.layer_poligon).ColorDistricts(minimff.counties,'color3')
        self.log.LogObj(minimff)

    def Anneal(self):
	#U-current solution
	#V-neighbour solution

    #1,2
        pareto = set()
        U = self.CreateInitialSolution()
        LayerManipulation(self.layer_poligon).ColorDistricts(U.counties,'color')

        #save the initial solution into the archive
        self.UpdatePareto(U,pareto)
        pareto.add(U)
        self.log.LogSolution(U,"Added to Pareto")

        t = self.initial_temperature
        t_num=0
        iterations = self.iterations

    #3-8

        while not self.frozen(t):
            t_num+=1
            logging.info("Temperature:%f(%d),Iterations:%d",t,t_num,iterations)
            for i in xrange(iterations):

                #neighbour solution of U
                V = self.NeighbourSolution(U)

                self.log.LogSolution(V,"Neighbour Solution")
                update = self.UpdatePareto(V,pareto)
                if update==1:

                    if len(pareto)>self.max_size_pareto:
                            U=random.sample(pareto,1)[0]
                            logging.info("Random choice from pareto")
                    else:
                    #the recently saved solution becomes the current solution

                        self.log.LogSolution(V,"Added to Pareto")
                        pareto.add(V)
                        U=V
                else:
                    if update==0:

                        V.weighted_obj = self.dot(U.weight_vectors,V.objective_values)
                        probability = self.probability(U.weighted_obj,V.weighted_obj,t)
                        logging.info("probability:%f",probability)
                        if random.uniform(0, 1)<= probability:
                        #in this case weight vectors for the solution weren't assigned

                            V.weight_vectors = U.weight_vectors
                            self.log.LogSolution(V,"Changed to current solution with probability %s" % probability)
                            U=V
                    else:
                        U=V

            t=self.reduceTemperature(t)
            iterations+=5

        logging.info('Temperature is frozen')
        self.showResults(pareto)
