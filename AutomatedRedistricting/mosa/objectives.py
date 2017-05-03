from __future__ import division

import logging
import yaml
import os.path
import math

class ObjFunc:

    def __init__(self):
        #load yaml
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml'),'r') as file_descriptor:
            data = yaml.load(file_descriptor)
            parameters = data.get('parameters')
            self.nr_of_districts = parameters['nr_of_districts']
            self.deviation = parameters['deviation']
            self.population_country =parameters['population_country']
            self.quota = self.population_country/self.nr_of_districts

    def c1(self,counties):
        sum=0
        for county in counties:
            fp_product = county.population/(self.deviation*(self.population_country/self.nr_of_districts))
            #logging.info("fp")
            #logging.info(fp_product)
            nr_of_districts = len(county.districts)
            for district in county.districts:
                    sp_product = district.population/county.population - 1/nr_of_districts
                    #logging.info("sp")
                    #logging.info(sp_product)
                    logging.debug("c1:")
                    logging.debug(fp_product*fp_product*sp_product*sp_product)
                    sum+=(fp_product*fp_product*sp_product*sp_product)
        return sum

    def c2(self,counties):
        sum=0
        for county in counties:
            for district in county.districts:
                sum+=((district.perimeter/(4*math.sqrt(district.area))-1))/10
        return sum

    def c1_(self,counties):
        sum=0
        for county in counties:
            for district in county.districts:
                sum+=(abs(district.population-self.quota))

        return sum/self.deviation

    def EvaluateObjectives(self,counties):
        #[C1(s),C2(s),..]
        return [f(counties) for f in [self.c1,self.c2]]
