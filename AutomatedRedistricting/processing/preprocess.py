from __future__ import division

from collections import defaultdict
import logging
from collections import defaultdict
from itertools import islice

#reterns an ojbect, which contains
#the population of the country and
#a dictinoary where
#key - groupid
#value - list of units
def presetForOpt(units,nr_of_districts):

    country_pop = 0
    grouped_units = defaultdict(list)

    for unit in units:
        grouped_units[unit.groupid].append(unit)
        country_pop+=unit.population

    #take every group and summarize the population of the units
    dict_pop = {groupid: sum(unit.population for unit in units) for (groupid,units) in grouped_units.iteritems() }

    return {'country_pop':country_pop,
            'nr_of_districts':nr_of_districts, #TODO: possibly you can leave this out
            'national_mean': country_pop/nr_of_districts,
            'grouped_units': grouped_units,
            'dict_pop' : dict_pop,
            'dict_units' : units}


def assignDistricts(dict_pop,national_mean,grouped_units,nr_of_districts):

    dict_assigned = {i: (dict_pop[i]//national_mean,dict_pop[i]/national_mean - dict_pop[i]//national_mean) for i in grouped_units.keys()}
    logging.info("Floors and Remainders:")
    logging.info(dict_assigned)

    assigned = 0
    for key, value in dict_assigned.iteritems():
        if value[0] == 1:
            dict_assigned[key] = (2,0)
            assigned+=2
        else:
            assigned+=value[0]

        units = len(grouped_units[key])
        if value[0] > units:
            assigned-=(value[0]-units)
            dict_assigned[key] = (units,0)
    #min and max district restrictions were set


    unassigned = nr_of_districts-assigned
    #assigne an additional district to counties with the highest fractional remainder
    if unassigned:
        dict_sorted = sorted(dict_assigned.items(), key=lambda (k, v): v[1],reverse=True)
        for key,value in list(islice(dict_sorted, unassigned)):
            dict_assigned[key] = (value[0]+1,value[1])


    assigned_districts = [assv for (assv,rem) in dict_assigned.values()]
    logging.info("Assigned Districts:%s", ','.join(str(x) for x in assigned_districts))
    #return the assigned values
    return assigned_districts
