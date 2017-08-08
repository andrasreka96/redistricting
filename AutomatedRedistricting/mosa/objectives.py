from __future__ import division

import logging
import yaml
import os.path
import math

class ObjFunc:

    def __init__(self,national_mean):
        self.national_mean=national_mean
        self.logger = logging.getLogger()

    def c1(self,counties):
        sum=0
        for county in counties:
            fp_product = county.population/(county.deviation*(self.national_mean))
            nr_of_districts = len(county.districts)
            for district in county.districts:
                    self.logger.debug("district %s with population:%f",district.unique_id,district.population)
                    sp_product = district.population/county.population - 1/nr_of_districts
                    objvalue = fp_product*fp_product*sp_product*sp_product*1000
                    sum+=objvalue
                    self.logger.debug("obj:%f",objvalue)
        return sum

    def c2(self,counties):

        sum=0
        for county in counties:
            self.logger.debug("county %d",county.id)
            for district in county.districts:
                val = (district.perimeter/(4*math.sqrt(district.area))-1)
                self.logger.debug("district %s:%f",district.unique_id,val)
                sum+=val
        return sum

    def EvaluateObjectives(self,counties,log=None):
        #[C1(s),C2(s),..]
        if log:
            self.logger.setLevel(logging.DEBUG)
            l = [f(counties) for f in [self.c1,self.c2]]
            self.logger.setLevel(logging.INFO)
            return l

        return [f(counties) for f in [self.c1,self.c2]]
