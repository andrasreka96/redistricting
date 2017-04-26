from __future__ import division
from collections import deque

import random
import logging
from collections import defaultdict
import yaml
import os.path
import math
from copy import deepcopy


from AutomatedRedistricting.model.county import County
from AutomatedRedistricting.model.solution import Solution
from AutomatedRedistricting.model.district import District
from AutomatedRedistricting.model.dis_build import DistrictBuilder
from AutomatedRedistricting.model.unit_build import UnitBuilder
from AutomatedRedistricting.layer_manipulation.layer import LayerManipulation
from AutomatedRedistricting.util.util import Log
import objectives

from PyQt4.QtGui import QColor

class MOSA:

    def __init__(self,layer_poligon,layer_poliline,layer_county ):
        #load yaml
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)

        attributes = data.get('attributes')
        parameters = data.get('parameters')
        #create util object with used layers
        self.layer_poligon=layer_poligon
        self.util = UnitBuilder(layer_poligon.getFeatures())

        #create dictionarie where
        #key - countyid
        #values - lists of features
        dictionarie = defaultdict(list)
        for feature in layer_poligon.getFeatures():
            dictionarie[feature[attributes['county_id']]].append(feature)
        self.dictionarie=dictionarie

        self.layer_county=layer_county
        self.counties_dict = {f[attributes['county_id']] : f[attributes['county_name']] for f in layer_county.getFeatures()}

        self.cooling_schedule = parameters['cooling_schedule']
        self.initial_temperature = parameters['initial_temperature']
        self.final_temperature = parameters['final_temperature']
        self.iterations = parameters['iterations']
        self.nr_of_counties = parameters['nr_of_counties']
        self.small_partition = parameters['small_partition']
        self.upper_limit = parameters['upper_limit']
        self.neighbourhood = parameters['neighbourhood']
        self.nr_of_districts_in_county = parameters['nr_of_districts_in_county']
        self.weight_vectors = parameters['weight_vectors']
        self.minnr_of_unit = parameters['minnr_of_unit']
        self.max_iter = parameters['max_iter']

        self.district_builder = DistrictBuilder(layer_poliline)
        self.objf = objectives.ObjFunc()

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
        util = UnitBuilder(features)
        units = set(util.units)

        unit_in_district=len(units)/nr_of_districts
        solution=[]

        #get color for every district
        #randomScheme = QgsRandomColorScheme()
        #colors=randomScheme.fetchColors(nr_of_districts)
        colors = [QColor("green").name(), QColor("magenta").name(), QColor("red").name(), QColor("orange").name(),
                      QColor("blue").name()]
        i=0;#number of created districts
        while units:
            logging.debug('Bilding distirict %d has started',i+1)
            #the district is divided into two set
            district=set()
            #this set stores the units which hasn't been chosen before
            #random_unit will be chosen firstly
            selectable_district=set()

            self.RandomChoise(units,selectable_district)

            j=0
            #stop when enough units were found or there are no more free neighbour
            while j<=unit_in_district-self.upper_limit and selectable_district:
                #get a random unit
                    random_unit = self.RandomChoise(selectable_district,district)
                #find out which neighbour unit is free
                    neighbour_units=random_unit.neighbours&units

                    new_neighbours_number=len(neighbour_units)
                    if new_neighbours_number:
                        selectable_district |= neighbour_units
                        units -= neighbour_units
                        j += new_neighbours_number
                        logging.debug('%d units has been added to district %d',new_neighbours_number+1,i+1)

            #units in new district
            new_district=district | selectable_district
            #don't create new district if there are enough of it or it is too small
            if i>=nr_of_districts or len(new_district)<unit_in_district/self.small_partition:
                #add units to an allready created district
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
                solution.append(District(i,str(county)+'_'+str(i),new_district,colors[i]))
                logging.debug('District %d has been added to the solution with %d units',i+1,len(new_district))
                #take the next district
                i+=1

        #make the final calculations for every istrict

        for s in solution:
            self.district_builder.BuildDistrict(s)
        return solution

    def CreateInitialSolution(self):
        #create districts for every county
        counties = []
        for countyid in range(1,self.nr_of_counties + 1):
            #get units in county
            units = self.dictionarie[countyid]
            logging.debug("Working on county %d(%d units)",countyid,len(units))
            district = self.CreateInitialCounty(self.nr_of_districts_in_county,units,countyid)
            logging.debug("County %d has been divided into %d districts",countyid,len(district))
            counties.append(County(countyid,self.counties_dict[countyid],district))

        objectives = self.objf.EvaluateObjectives(counties)
        LayerManipulation(self.layer_poligon).ColorDistricts(counties,'color')
        #Log().LogSolution(Solution(counties,objectives))
        return Solution(counties,objectives)

    def BFS(self,district):
        #Decides whether a given district is connected 
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


    def MoveUnits2(self,solution,change):
        #random county where the changes will be made
        county  = random.choice(solution.counties)
        units_to_move=set()

        #random district
        stop = False
        iteration = 0
        while not stop and iteration<=self.max_iter:
            #move units from d1 to d2
            (d1,d2) = random.sample(county.districts,2)
            for unit in d2.borders:
                units_to_move |= unit.neighbours & d1.borders

            if units_to_move:
                stop = True

            iteration +=1

        #don't move more than is required
        if len(units_to_move)>change:
             units_to_move = set(random.sample(units_to_move,change))

        #can't leave a district empty
        if len(d1.units-units_to_move) > self.minnr_of_unit:

            #move = set()
            #for unit in units_to_move:
                #exceptu = d1.units-set([unit])
                #for neighbour in unit.neighbours:
                    #if not neighbour.neighbours & exceptu:
                        #break
                #else:
                    #move.add(unit)


            if self.BFS(District(1,'',d1.units-units_to_move,'')):

                d2.extand(units_to_move)
                d1.remove(units_to_move)

                self.district_builder.BuildDistrict(d1)
                self.district_builder.BuildDistrict(d2)


    def NeighbourSolution(self,solution):
        new_solution = deepcopy(solution)
        log = Log()
        for depth in self.neighbourhood:
            self.MoveUnits2(new_solution,depth)
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

    def UpdatePareto(self,solution,pareto):
        (dominated,dominates) = self.Dominations(solution,pareto)

        if not dominated and not dominates:

            pareto.add(solution)
            solution.weight_vectors = random.sample(self.weight_vectors,1)[0]

            #weighted objective function
            solution.weighted_obj = self.dot(solution.weight_vectors,solution.objective_values)
            logging.info("Solution with  values %f,%f,%f was added to pareto set",solution.objective_values[0],solution.objective_values[1],solution.weighted_obj)
            return True

        if dominates:
            removable_solution = random.sample(dominates,1)[0]
            solution.weight_vectors = removable_solution.weight_vectors
            solution.weighted_obj = self.dot(solution.weight_vectors,solution.objective_values)
            pareto.remove(removable_solution)
            pareto.add(solution)
            logging.info("Solution with objective values %f,%f was replaced",solution.objective_values[0],solution.objective_values[1])
            return True

        logging.info("Solution with objective values %f,%f wasn't added",solution.objective_values[0],solution.objective_values[1])
        return False

    def probability(self,obj1,obj2,t):
        try:
            ans = math.exp((obj1-obj2)/t)
        except OverflowError:
            ans = 0

        return ans

    def Anneal(self):
    #1,2
        pareto = set()
        U = self.CreateInitialSolution()
        LayerManipulation(self.layer_poligon).ColorDistricts(U.counties,'color')
        self.UpdatePareto(U,pareto)
        t = self.initial_temperature
    #3-8

        while not self.frozen(t):
            logging.info("Temperature:%f",t)
            for i in xrange(self.iterations):
                    logging.info("Iteration:%d",i)
                    #neighbour solution of u
                    V = self.NeighbourSolution(U)
                    logging.debug("Neighbour solution with objective values:%s",','.join(str(x) for x in V.objective_values))
                    if self.UpdatePareto(V,pareto):
                        U=V
                        #if len(pareto_set)>MAX:
                            #U=random.sample(pareto_set)
                    else:
                        V.weighted_obj = self.dot(U.weight_vectors,V.objective_values)
                        #logging.info("weighted_obj:%f",V.weighted_obj)
                        probability = self.probability(U.weighted_obj,V.weighted_obj,t)
                        #logging.info("probability:%f",probability)
                        if random.uniform(0, 1)<= probability:
                        #in this case weight_vector for the solution wasn't assigned
                            logging.info("Current solution was changed according to probability %f",probability)
                            V.weight_vectors = U.weight_vectors
                            U=V

            t=self.reduceTemperature(t)

        logging.info('Temperature is frozen')
        minims = random.sample(pareto,1)[0]
        for s in pareto:
            logging.info("fit:%f",s.weighted_obj)
            if minims.weighted_obj>s.weighted_obj:
                minims = s

        logging.info('fit:%f',minims.weighted_obj)
        LayerManipulation(self.layer_poligon).ColorDistricts(minims.counties,'color2')
