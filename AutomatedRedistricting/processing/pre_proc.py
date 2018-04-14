from __future__ import division


import logging
import yaml
import os.path

from collections import defaultdict
from itertools import islice



class PreProcessing:
    def __init__(self,layer_poligon,layer_poliline ):
        #load yaml
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)

        attributes = data.get('attributes')
        self.attrib_join_id = attributes['join_id']
        self.attrib_pop = attributes['attribute_population']
        parameters = data.get('parameters')
        self.nr_of_districts = parameters['nr_of_districts']

        #save used layers
        self.layer_poligon=layer_poligon

        #create dictionary where
        #key - regionid
        #values - lists of features
        self.dict_units = defaultdict(list)


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

        logging.info("Population in regions:")
        logging.info(self.dict_pop)

        #init population related stuff
        self.national_mean = self.population_country/self.nr_of_districts

    def AssignDistricts(self):

        dict_assigned = {i: (self.dict_pop[i]//self.national_mean,self.dict_pop[i]/self.national_mean - self.dict_pop[i]//self.national_mean) for i in range(1,self.nr_of_regions + 1)}
        logging.info("Floors and Remainders:")
        logging.info(dict_assigned)
        for key,value in dict_assigned.iteritems():
            print(value[0])

        assigned = 0
        for key, value in dict_assigned.iteritems():
            if value[0] == 1:
                dict_assigned[key] = (2,0)
                assigned+=2
            else:
                assigned+=value[0]

            units = len(self.dict_units[key])
            if value[0] > units:
                assigned-=(value[0]-units)
                dict_assigned[key] = (units,0)
        #min and max district restrictions were set


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
