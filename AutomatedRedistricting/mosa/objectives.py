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
            self.population_country =parameters['population_country']
            self.quota = self.population_country/self.nr_of_districts
            self.logger = logging.getLogger()

    def c1(self,counties):
        sum=0
        for county in counties:
            fp_product = county.population/(county.deviation*(self.population_country/self.nr_of_districts))
            self.logger.debug("county %d fp:%f",county.id,fp_product)
            nr_of_districts = len(county.districts)
            for district in county.districts:
                    sp_product = district.population/county.population - 1/nr_of_districts
                    self.logger.debug("district %s fp:%f",district.unique_id,sp_product)
                    sum+=(fp_product*fp_product*sp_product*sp_product)*100
                    self.logger.debug("product:%f",fp_product*fp_product*sp_product*sp_product)
        return sum

    def c2(self,counties):

        sum=0
        for county in counties:
            self.logger.debug("county %d",county.id)
            for district in county.districts:
                val = (district.perimeter/(4*math.sqrt(district.area))-1)
                self.logger.debug("district %s:%f",district.unique_id,val)
                sum+=val/10
        return sum

    def EvaluateObjectives(self,counties,log=None):
        if log:
            self.logger.setLevel(logging.DEBUG)
            l = [f(counties) for f in [self.c1,self.c2]]
            self.logger.setLevel(logging.INFO)
            return l

        return [f(counties) for f in [self.c1,self.c2]]
