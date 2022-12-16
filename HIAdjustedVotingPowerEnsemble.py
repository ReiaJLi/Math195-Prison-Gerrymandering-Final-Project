# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 22:04:10 2022

@author: 15202
"""


import shapely
import fiona
import networkx as nx
import matplotlib.pyplot as plt
from numpy import random
import gerrychain   
from gerrychain import Graph, Partition, proposals, updaters, constraints, accept, MarkovChain
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
from gerrychain.proposals import recom
from gerrychain.accept import always_accept
from functools import partial
import geopandas as gpd
import pandas as pd



# Goal: Make an ensemble of plans using the adjusted population data 
#that reallocates incarcerated people to their last known address
#and then keep track of the actual voting power of the people 
#who can vote in each district 



#STEP 1: MAKE DUAL GRAPH FROM SHAPEFILES

#Import shapefile and population data 
hawaii_bg_dg_filename = 'hawaii_bg_dg'
infile = open(hawaii_bg_dg_filename,'rb')
new_dg = pickle.load(infile)
infile.close()
print(new_dg==hawaii_bg_dg_filename)
print(type(new_dg))

#Making sure the new dual graph is connected
print(nx.is_connected(new_dg))




print(len(new_dg.nodes))
print(len(new_dg.edges))

print(new_dg.nodes()[150]['cvap'])


#STEP 3: MAKE ENSEMBLE 

# Get total unadjusted population
tot_pop = 0
for v in new_dg.nodes():
    tot_pop = tot_pop + new_dg.nodes()[v]['adjtotal']

print("Total Population: ", tot_pop)

# Initial districting plan using recursive_tree_part
num_dist = 51 # Number of Legislative Districts in Hawaii for State House, each district elects one Representative 
ideal_pop = tot_pop/num_dist
pop_tolerance = 0.9 #This means that the population balance within each district will be balanced within 10% of each other

#Specify initial redistricting plan that is the current AZ plan 
#by specifying each node in the initial_plan 
#as the district that it is in the file 
initial_plan = {}
for v in new_dg.nodes():
    initial_plan[v] = int(new_dg.nodes()[v]['district_h'])

print(initial_plan)


# Now create a partition. A partition is EXPLAINNNNN 

initial_partition = Partition (
    new_dg, #dual graph 
    assignment = initial_plan, 
    updaters = {
        "our cut edges": cut_edges, #cut_edges is a built-in function in gerrychain 
                                    #that lists all the cutedges of a plan 
         "district population": Tally("adjtotal", alias = "district population"),                           
                #adds up unadjusted population for each district 
        "citizen voting age population": Tally("cvap", alias = "citizen voting age population")
                #adds up the citizen voting age population in each district 
                      
         }
    )

print(initial_partition)
print(initial_partition["our cut edges"])
print(len(initial_partition["our cut edges"]))
print(initial_partition["district population"])
print(initial_partition["citizen voting age population"])


#Now to make one step: 
rw_proposal = partial(recom, #how you make a new districting plan 
                      pop_col = "adjtotal", #what the population attribute is called 
                      pop_target = ideal_pop, #population a district should have
                      epsilon = pop_tolerance, #how much a district pop can vary from ideal
                      node_repeats = 1 #how many times you attempt something before restarting and drawing a new spanning tree 
                      )

## Constraint on population: stay within pop_tolerance of ideal

population_constraint = constraints.within_percent_of_ideal_population(
    initial_partition, #initial partition
    pop_tolerance, #how far away from ideal population of a district can be 
    pop_key = "district population") #name of the updater that looks at population constraint 



## Creating the chain
# Set sup the chain, but doesn't run it!
our_random_walk = MarkovChain(
    proposal = rw_proposal, #how next plan is made
    constraints = [population_constraint], #checking that the next plan is valid
    accept = always_accept, #needs to be here
    initial_state = initial_partition, #starting point
    total_steps = 20 #number of steps in the random walk 
    )

# What ensemble we want to build
hi_adjvotingpower_ensemble = [] 
cutedge_ensemble = []

# This actually runs the random walk!
for part in our_random_walk: #a part is equivalent to one redistricting plan 
    hi_adjvotingpowerlist = []
    for i in range(num_dist):
        hi_adjvotingpower = 1/part["citizen voting age population"][i + 1] #measures the voting power in each district by taking 1/(citizen voting age population0 in that district
        hi_adjvotingpowerlist.append(hi_adjvotingpower)
        
    hi_adjvotingpower_difference = max(hi_adjvotingpowerlist) - min(hi_adjvotingpowerlist) #measures the difference between the greatest and smallest voting power in the plan 
    hi_adjvotingpower_ensemble.append(hi_adjvotingpower_difference) #adds the difference to the ensemble 
    
    cutedge_ensemble.append(len(part["our cut edges"]))   
    
plt.figure()
plt.hist(cutedge_ensemble)
plt.title("HI Adjusted Ensemble Number of Cutedges of 20,000 Plans")
plt.xlabel("Number of Cutedges")
plt.ylabel("Number of Plans")
plt.show()

plt.figure()
plt.hist(hi_adjvotingpower_ensemble)
plt.title("HI Adjusted Voting Power Ensemble of 20,000 Plans")
plt.xlabel("Greatest Difference in Voting Power")
plt.ylabel("Number of Plans")
plt.show()

plt.boxplot(hi_adjvotingpower_ensemble)
plt.title("HI Adjusted Voting Power Boxplot")
plt.ylabel("Greatest Difference in Voting Power")
plt.xlabel("Ensemble of 20,000 plans")
plt.show()