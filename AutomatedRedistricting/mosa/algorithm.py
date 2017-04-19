from __future__ import division

import random
import logging
from collections import defaultdict
import yaml
import os.path
import math

from AutomatedRedistricting.model.county import County
from AutomatedRedistricting.model.district import District
from AutomatedRedistricting.model.dis_build import DistrictBuilder
from AutomatedRedistricting.model.unit_build import UnitBuilder

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
        self.nr_of_districts_in_county = parameters['nr_of_districts_in_county']
        self.small_partition = parameters['small_partition']
        self.upper_limit = parameters['upper_limit']
        self.neighbourhood = parameters['neighbourhood']
        self.nr_of_districts = parameters['nr_of_districts']
        self.deviation = parameters['deviation']
        self.population_country =parameters.['population_country']

        self.district_builder = DistrictBuilder(layer_poliline)
        self.district_dict = {}


    def c1(self,counties):
        sum=0
        logging.debug("C1")
        for county in counties:
            fp_product = 100*county.population/(self.deviation*(self.population_country/self.nr_of_districts))
            csum=0
            for district in county.districts:
                    sp_product = district.population/county.population - 1/self.nr_of_districts_in_county
                    csum+=fp_product*fp_product*sp_product*sp_product
                    logging.debug("district %s:%.2f",district.unique_id,csum)
            sum+=csum
        return sum

    def c2(self,counties):
        sum=0
        logging.debug("C2")
        for county in counties:
            csum=0
            for district in county.districts:
                csum+=(district.perimeter/(4*math.sqrt(district.area))-1)
                logging.debug("district %s:%.2f",district.unique_id,csum)
            sum+=csum
        return sum

    def f(self,counties,objective_f,weights):
        fs = [f(counties) for f in objective_f]
        #returns the scalar product of the objective functions and their weights
        return self.dot(fs,weights)

    def prob(self,counties):
        objective_f = [self.c1,self.c2]
        w=[0.5,0.5]
        return self.f(counties,objective_f,w)

    def DistrictNear(self,units,util,solution):
        for i in units:
            unit = set(util.getUnitsById(i.neighbours))
            for district in solution:
                if unit & district.borders:
                    return district.id

    def CreateInitialSolution(self,nr_of_districts,features,county):
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
            self.district_dict[s.unique_id]=s

        return solution

    def CreateInitialDistricts(self):
        #create districts for every county
        counties = []
        for countyid in range(1,self.nr_of_counties + 1):
            #get units in county
            units = self.dictionarie[countyid]
            logging.debug("Working on county %d(%d units)",countyid,len(units))
            districts = self.CreateInitialSolution(self.nr_of_districts_in_county,units,countyid)
            logging.debug("County %d has been divided into %d districts",countyid,len(districts))
            counties.append(County(countyid,self.counties_dict[countyid],districts))

        return counties

    def NeighbourUnit(self,u1,u2):
        if u1.id in u2.neighbours:
            return True
        return False

    def UpdateAdjacencyList(self,border_pairs,units):
        new_border = [pair for unit in units for pair in border_pairs if unit.id!=pair[0].id or unit.id!=pair[1].id]
        for unit in units:
            neighbours = self.util.getUnitsById(unit.neighbours)
            for n in neighbours:
                new_border.append(unit)

        return new_border

    def AdjacencyList (self,counties):
        #for county in solution[0]:
        #get the list of districts
        logging.debug("Building adjacency list")
        border_pairs = []
        for county in counties:
            borderunits = [unit for district in county.districts for unit in district.borders]
            for u1 in borderunits:
                for u2 in borderunits:
                    if u2.district_id!=u1.district_id and u2.id in u1.neighbours and (u2,u1) not in border_pairs:
                        border_pairs.append((u1,u2))
        logging.debug("Adjacency list was constructed")
        return border_pairs

    def NeighboursInDepth(self,unit,depth):
    #returns unit neighbours in a given depth

        district = self.district_dict[unit.district_id]
        units = district.unitids
        u = unit
        neighbours = set([unit.id])
        while depth>0:
            neighbourhood=u.neighbours&units
            neighbours|=neighbourhood
            depth-=depth
            u = self.util.getUnitsById(random.sample(neighbourhood,1))[0]

        units-=neighbours

        #list of units that will be moved
        neighbour_units = self.util.getUnitsById(neighbours)
        for unit in self.util.getUnitsById(units):
            if not unit.neighbours & units:
                neighbour_units.append(unit)
        return self.util.getUnitsById(neighbours)

    def MoveUnits(self,depth,border_pairs):

        #chose randomly two district for make change
        units = random.sample(border_pairs,1)[0]
        fromindex = random.randint(0,1)
        u_from = units[fromindex]
        u_to = units[abs(fromindex-1)]

        unitstomove = self.NeighboursInDepth(u_from,depth)
        self.district_dict[u_to.district_id].extand(set(unitstomove))
        self.district_dict[u_from.district_id].remove(set(unitstomove))

        d1 = self.district_dict[u_from.district_id]
        d2 = self.district_dict[u_to.district_id]
        self.district_builder.BuildDistrict(d1)
        self.district_builder.BuildDistrict(d2)

        #adjacency list has to be changed
        border_pairs = self.UpdateAdjacencyList(border_pairs,unitstomove)

    def NeighbourSolution(self,counties):
        border_pairs = self.AdjacencyList(counties)

        for change in self.neighbourhood:
            self.MoveUnits(change,border_pairs)


    def dot(self,x,y):
        return sum([a*b for a,b in zip(x,y)])

    def frozen(self,t):
        return t<=self.final_temperature

    def reduceTemperature(self,t):
        return t*self.cooling_schedule

    def updatePareto(U):
        if not dominate(U) and not dominated(U):
            addToPareto(U)
            assignWeight(U)
        else :
            if dominates(U):
                D = dominatedBy(U)
                C = random(D)
                C = U
    def anneal(self):
    #1,2

        #weight_vectors = GenerateWeightVectors(number_of_nondominated_solutions)
        #U.s = CreateInitialSolution()
        #U.f = evaluate(U) # [C1(U),C2(U),..,Cn(U)]
        #U.w = updatePareto(U)
        #U.deltaf = dot(U.w,U.f)

        t = self.initial_temperature
        logging.info("Iterations has been started")
    #3-8
        while not self.frozen(t):
            logging.info("Iterations has been started")
            for i in xrange(self.iterations):
                if False:
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
                        if random.uniform(0, 1)<=probability(V.deltaf,t):
                            U=V

            t=self.reduceTemperature(t)

        logging.info('Temperature is frozen')
