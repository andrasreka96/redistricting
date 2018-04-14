from __future__ import division
from collections import deque

import random
import logging
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
from AutomatedRedistricting.processing.pre_proc import PreProcessing
from AutomatedRedistricting.processing.post_proc import PostProcessing


import objectives

from PyQt4.QtGui import QColor

class MOSA:

    def __init__(self,layer_poligon,layer_poliline ):
        pre_processing = PreProcessing(layer_poligon,layer_poliline)
        pre_processing.BuildRegion()

        self.objf = objectives.ObjFunc(pre_processing.national_mean)

        self.national_mean = pre_processing.national_mean
        self.nr_of_regions = pre_processing.nr_of_regions
        self.dict_units = pre_processing.dict_units
        self.dict_pop = pre_processing.dict_pop
        self.district_in_counties = pre_processing.AssignDistricts()


        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            #read config file
            data = yaml.load(file_descriptor)

        parameters = data.get('parameters')

        self.cooling_schedule = parameters['cooling_schedule']
        self.initial_temperature = parameters['initial_temperature']
        self.final_temperature = parameters['final_temperature']
        self.iterations = parameters['iterations']
        self.iterations_increment = parameters['iterations_increment']
        self.small_partition = parameters['small_partition']
        self.upper_limit = parameters['upper_limit']
        self.neighbourhood = parameters['neighbourhood']
        self.weight_vectors = parameters['weight_vectors']
        self.minnr_of_unit = parameters['minnr_of_unit']
        self.max_iter = parameters['max_iter']
        self.max_size_pareto = parameters['max_size_pareto']
        self.nr_of_districts = parameters['nr_of_districts']

        self.attributes = data.get('attributes')
        self.district_builder = DistrictBuilder(layer_poliline,self.attributes['attribute_id_poliline'])

        #for logging
        self.log =  Log(ObjFunc(self.national_mean))
        self.layer_manipulation = LayerManipulation(layer_poligon)

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

    def CreateInitialCounty(self,nr_of_districts,features,regionid):
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

            #don't create new district if there are enough of it or it would be too small
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

                solution.append(District(i,str(regionid)+'_'+str(i),new_district,self.colors[regionid-1][i]))
                logging.debug('District %d has been added to the solution with %d units',i+1,len(new_district))

                #take the next district
                i+=1

        #make the final calculations for every district
        for s in solution:
            self.district_builder.BuildDistrict(s)
        return solution

    def CreateInitialSolution(self):

        counties = []

        max_val = max(self.district_in_counties)
        light_value = 51-max_val
        if max_val > 10:
            light_value/=(max_val/10)

        color_obj = Color()

        #create a base color for every region
        base_colors = color_obj.generateColors(self.nr_of_regions)
        colors = []
        for i in range(0,self.nr_of_regions):
                #colors.append(color_obj.generateColors(self.district_in_counties[i]))
            colors.append(color_obj.lighter(base_colors[i],int(self.district_in_counties[i]),light_value))

        self.colors =  color_obj.RGBtoHex(colors)
        for countyid in range(1,self.nr_of_regions + 1):
            #get units in county
            units = self.dict_units[countyid]

            district = self.CreateInitialCounty(self.district_in_counties[countyid-1],units,countyid)

            #determine the allowed deviations in each county

            #differene between the national and state mean
            diff = abs(self.dict_pop[countyid]/self.district_in_counties[countyid-1]-self.national_mean)

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

        #return the solution created by counties
        return Solution(counties,self.objf.EvaluateObjectives(counties))

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
            if d2.population > d1.population:
                acc = d1
                d1 = d2
                d2 = acc

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

    def probability(self,obj1,obj2,t):
        diff=obj1-obj2
        if diff>=0:
            return 1
        try:
            ans = math.exp(diff/t)
        except OverflowError:
            ans = 0
        return ans

    def dominates(self,regions1,regions2):
        dominates = True

        for r1,r2 in zip(self.objf.EvaluateObjectives(regions1),self.objf.EvaluateObjectives(regions2)):
            dominates = dominates and r1<r2 #region1 dominates
        return dominates

    def dominatesSet(self,solution,pareto):
        dominates = []

        for s in pareto:
            if self.dominates(solution.counties,s.counties):
                dominates.append(s)

        return dominates

    def dominatedSet(self,solution,pareto):
        dominated = False

        i=0
        #iter over the pareto set until solution isn't dominated
        for s in pareto:
            if dominated:
                break
            dominated = dominated or self.dominates(s.counties,solution.counties)

        return dominated



    def merge(self,s1,s2):
        #merge s2 into s1

        for i in range(0,self.nr_of_regions):
            r1 = s1.counties[i]
                #if s2's region dominates merge into s1
            r2 = s2.counties[i]

            if self.dominates([r2],[r1]):
                s1.counties[i] = SolutionBuilder().CopyCounty(r2)
        #set the new objective values accoirding to the merged regions
        s1.objective_values = self.objf.EvaluateObjectives(s1.counties)

    def UpdatePareto(self,solution,pareto):

        if not dominated and not dominates:
            return 1

        if dominates:

            removable_solution = self.ChooseBetweenDominated(solution,dominates)
            solution.weight_vectors = removable_solution.weight_vectors
            solution.weighted_obj = self.dot(solution.weight_vectors,solution.objective_values)
            removable_solution = solution
            self.log.LogSolution(removable_solution,"New solution")
            return 2

        return 0

    def Anneal(self):
	#U-current solution
	#V-neighbour solution

    #1,2
        pareto = set()
        U = self.CreateInitialSolution()
        self.layer_manipulation.ColorDistricts(U.counties,'color')

        #save the initial solution into the archive
        pareto.add(U)
        #assign a weight vector
        U.weights(random.sample(self.weight_vectors,1)[0])
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
                V.temperature = t
                V.iter = i+1
                self.log.LogSolution(V,"Neighbour Solution")

                dominates = self.dominatesSet(V,pareto)
                if dominates:

                    removable_solution = self.ChooseBetweenDominated(V,dominates)
                    V.weights(removable_solution.weight_vectors)
                    removable_solution = V
                    self.log.LogSolution(V,"New solution")
                    U=V

                else:
                    #when V doesn't dominate any solution from the pareto set
                    if self.dominatedSet(V,pareto):

                        V.weights(U.weight_vectors)
                        probability = self.probability(U.weighted_obj,V.weighted_obj,t)
                        logging.info("probability:%f",probability)
                        if random.uniform(0, 1)<= probability:
                            self.log.LogSolution(V,"Changed to current solution with probability %s" % probability)
                            U=V
                    else:
                        if len(pareto)>self.max_size_pareto:
                            self.merge(U,V)
                            U.temperature = t
                            U.iter = i+1
                            self.log.LogSolution(U,"Solution merged")
                        else:
                        #add solution to pareto
                            V.weights(random.sample(self.weight_vectors,1)[0])
                            pareto.add(V)
                            self.log.LogSolution(V,"Added to Pareto")
                            U=V

            t=self.reduceTemperature(t)
            iterations+=self.iterations_increment
            #start the next iterations with a solution randomly selected from the Pareto set
            U = random.sample(pareto,1)[0]

        logging.info('Temperature is frozen')
        PostProcessing(pareto,self.objf,self.log).showResults(self.layer_manipulation,[[0.5,0.5],[0.8,0.2]])
