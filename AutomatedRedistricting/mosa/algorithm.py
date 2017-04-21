from __future__ import division

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

        self.district_builder = DistrictBuilder(layer_poliline)
        self.objf = objectives.ObjFunc()

    def DistrictNear(self,units,util,solution):
        for i in units:
            unit = set(util.getUnitsById(i.neighbours))
            for district in solution:
                if unit & district.borders:
                    return district.id

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
            while j<=unit_in_district-self.upper_limit and selectable_district:

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
                        logging.debug('%d units has been added to district %d',new_neighbours_number+1,i+1)

            #units in new district
            new_district=district | selectable_district

            #don't create new district if there are enough of it or it is too small
            if i>=nr_of_districts or len(new_district)<unit_in_district/self.small_partition:
                #add units to an allready created district
                ind=self.DistrictNear(new_district,util,solution)
                solution[ind].extand(new_district)
                logging.debug('District %d:expanded by %d new units',ind,len(new_district))
            else:
            #create district and add to the solution
                solution.append(District(i,new_district,colors[i],county))
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

        return Solution(counties,self.objf.EvaluateObjectives(counties))

    def NeighbourUnit(self,u1,u2):
        if u1.id in u2.neighbours:
            return True
        return False

    def NeighboursInDepth(self,district,unit,depth):
        #returns unit neighbours in a given depth

        units = district.unitids
        u = unit
        neighbours = set([unit.id])
        while depth>0:
            neighbourhood=u.neighbours&units
            neighbours|=neighbourhood
            depth-=depth
            if neighbourhood:
                u = self.util.getUnitsById(random.sample(neighbourhood,1))[0]

        return self.util.getUnitsById(neighbours)

    def FindConnectedUnit(self,unit_to_move,county,district1):
        for district in county.districts:
            if district1.id != district.id:
                for unit in district.borders:
                    if self.NeighbourUnit(unit_to_move,unit):
                        return unit

    def MoveUnits(self,solution,depth):

        district1=random.choice(solution.district_dict.values())
        county  = solution.counties[district1.county-1]
        unit_to_move = random.sample(district1.borders,1)[0]
        unit_to_append = self.FindConnectedUnit(unit_to_move,county,district1)

        if unit_to_append:
            district2=solution.district_dict[unit_to_append.district_id]
            unitstomove = set(self.NeighboursInDepth(district1,unit_to_move,depth))

            district2.extand(unitstomove)
            district1.remove(unitstomove)

            self.district_builder.BuildDistrict(district1)
            self.district_builder.BuildDistrict(district2)
            solution.changeDistrict(district1)
            solution.changeDistrict(district2)

    def NeighbourSolution(self,solution):
        new_solution = deepcopy(solution)
        for depth in self.neighbourhood:
            self.MoveUnits(new_solution,depth)
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
                    #logging.info("Neighbour solution with objective values:%s",','.join(str(x) for x in V.objective_values))
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
