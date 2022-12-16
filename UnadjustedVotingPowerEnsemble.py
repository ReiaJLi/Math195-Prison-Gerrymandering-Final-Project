# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 14:13:19 2022

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




# Goal: Make an ensemble of plans using the current, unadjusted population data 
#that counts incarcerated people where they are incarcerated
#and then keep track of the actual voting power of the people 
#who can vote in each district 


#STEP 1: MAKE DUAL GRAPH FROM SHAPEFILES

#Merge shapefile and population data 

#import shapefile of block group data
az_bg_shpfile = gpd.read_file('AZ_Block_groups_2022.zip')

#check what info it has in its rows and colums 
print(az_bg_shpfile.head())
print(az_bg_shpfile.columns)

print(az_bg_shpfile['GEOID'])

#turn GEOID into floats so that it can match with the other data 
az_bg_shpfile_float = az_bg_shpfile
az_bg_shpfile_float['GEOID'] = az_bg_shpfile_float['GEOID'].astype(float)


print(az_bg_shpfile_float[1:10]['GEOID'])
#import the spreadsheet with prison population reallocation data 
az_bg_prisondata = pd.read_csv('AZ_prisoner_BG_adjusted_data_with_cvap.csv')
print(az_bg_prisondata.head())
print(az_bg_prisondata.columns)

#merge the shapefile and the spreadsheet with population data 
# merge = combine the two data sets
# on = what columns you're lining up
# how = "left" means keep all observations in city_data
az_merge = az_bg_shpfile_float.merge(az_bg_prisondata, on = ['GEOID'], how = "left")
print(az_merge.head())
print(az_merge.columns)

print(az_bg_shpfile_float.shape[0])
print(az_bg_prisondata.shape[0])
print(az_merge.shape[0])

#check to make sure there is data in the merged file
print(az_merge[1:10]['COUNTYFP'])
print(az_merge[1:10]['cvap'])



#STEP 2: NOW MAKE THE DUAL GRAPH 

#az refers to Arizona
#bg refers to census block groups
#building the dual graph
az_bg_dg = Graph.from_geodataframe(az_merge, ignore_errors = False)

#Check the properties of the dual graph
#is connected checks if you can get to every node through an edge 
#number of nodes matches the number of block groups
#number of edges measures the amount of edges, which is based on the adjacency between nodes 
print("Is this dual graph connected? ", nx.is_connected(az_bg_dg)) 
print("Number of Nodes: ", len(az_bg_dg.nodes()))
print("Number of Edges: ", len(az_bg_dg.edges()))

print(az_bg_dg.nodes()[0]) #what info is stored at node 0 

#STEP 3: MAKE ENSEMBLE 

# Get total unadjusted population
tot_pop = 0
for v in az_bg_dg.nodes():
    tot_pop = tot_pop + az_bg_dg.nodes()[v]['total']

print("Total Population: ", tot_pop)

# Initial districting plan using recursive_tree_part
num_dist = 30 # Number of Legislative Districts in Arizona for State House and Senate, each district elects one Senator and two Reps 
ideal_pop = tot_pop/num_dist
pop_tolerance = 0.1 #This means that the population balance within each district will be balanced within 10% of each other

#Specify initial redistricting plan that is the current AZ plan 
#by specifying each node in the initial_plan 
#as the district that it is in the file 
initial_plan = {}
for v in az_bg_dg.nodes():
    initial_plan[v] = int(az_bg_dg.nodes()[v]['district'])

print(initial_plan)


# Now create a partition. A partition is EXPLAINNNNN 

initial_partition = Partition (
    az_bg_dg, #dual graph 
    assignment = initial_plan, 
    updaters = {
        "our cut edges": cut_edges, #cut_edges is a built-in function in gerrychain 
                                    #that lists all the cutedges of a plan 
         "district population": Tally("total", alias = "district population"),                           
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
                      pop_col = "total", #what the population attribute is called 
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
    total_steps = 10000 #number of steps in the random walk 
    )

# What ensemble we want to build
unadjvotingpower_ensemble = [] 
cutedge_ensemble = []

# This actually runs the random walk!
for part in our_random_walk: #a part is equivalent to one redistricting plan 
    unadjvotingpowerlist = []
    for i in range(num_dist):
        unadjvotingpower = 1/part["citizen voting age population"][i + 1] 
        #measures the voting power in each district by taking 1/(citizen voting age population) in that district
        unadjvotingpowerlist.append(unadjvotingpower)
        
    unadjvotingpower_difference = max(unadjvotingpowerlist) - min(unadjvotingpowerlist) 
    #measures the difference between the greatest and smallest voting power in the plan 
    unadjvotingpower_ensemble.append(unadjvotingpower_difference) #adds the difference to the ensemble 
    
    cutedge_ensemble.append(len(part["our cut edges"]))   
    
plt.figure()
plt.hist(cutedge_ensemble)
plt.title("AZ Unadjusted Ensemble Number of Cutedges for 10,000 Plans")
plt.xlabel("Number of Cutedges")
plt.ylabel("Number of Plans")
plt.show()

plt.figure()
plt.hist(unadjvotingpower_ensemble)
plt.title("AZ Unadjusted Voting Power Ensemble for 10,000 Plans")
plt.xlabel("Greatest Difference in Voting Power")
plt.ylabel("Number of Plans")
plt.show()

plt.boxplot(unadjvotingpower_ensemble)
plt.title("AZ Unadjusted Voting Power Boxplot")
plt.ylabel("Greatest Difference in Voting Power")
plt.xlabel("Ensemble of 10,000 plans")
plt.show()

