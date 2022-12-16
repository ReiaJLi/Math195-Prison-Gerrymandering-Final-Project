# Math195-Prison-Gerrymandering-Final-Project
AZ_Block_Groups_2022 = the census shapefile with geographic data on AZ block groups

AZ_prisoner_BG_adjusted_data_with_cvap = the demographic data with adjusted and unadjusted population from Redistricting Data Hub 

UnAdjusted and AdjustedVotingPowerEnsemble = code to create ensemble of plans for AZ to examine voting power

HIUnAdjusted and HIAdjustedVotingPowerEnsemble = code to create ensemble of plans for HI to examine voting power

az_merge.zip = Arizona shapefile with block group data and demographic data

hawaii_bg_dg = hawaii dual graph by block group used in voting power analysis

AZ_Markov_Chain_bg_adj.py = Code for running short bursts on adjusted population data in Arizona

AZ_Markov_Chain_bg_unadj.py = Code for running short bursts on unadjusted population data in Arizona

AZ_prisoner_BG_adjusted_data_with_cvap.csv = CSV file for Arizona adjusted population data with CVAP population

HI_Markov_Chain_bl_adj.py = Code for running short bursts on adjusted population data in Hawaii

HI_Markov_Chain_bl_unadj.py = Code for running short bursts on unadjusted population data in Hawaii

Hawaii_block_returning_data_calculations.csv = CSV file with adjusted and unadjusted population data at block level in Hawaii. This is used in hawaii_final_gerry.py

Hawaii_block_returning_data_calculations.xlsx = Full excel file with adjusted and unadjusted population data at block level in Hawaii. Includes calculations used to disaggregate other race category

az_final_gerry.py = Tests whether Arizona population data was properly imported into Python. Also fused Census block shapefile and population data to create az_merge.zip 


az_shortbursts_results_aggregated_adj.csv = Arizona short bursts results for adjusted population used in AZ_Markov_Chain_bg_adj.py to create box plot

az_shortbursts_results_aggregated_unadj.csv = Arizona short bursts results for unadjusted population used in AZ_Markov_Chain_bg_unadj.py to create box plot

hi_bg_dg_edits.py = Pickled dual graph that is used in HI_Markov_Chain_bl_adj.py and HI_Markov_Chain_bl_unadj.py. Must unzip file before running the pickle code.

hi_bg_dg_edits.py = Adding edges and removing nodes at block group level. Creates hawaii_bg_dg.zip 

hi_bg_merge.zip = Block group level population shapefile used for Voting Power Analysis for Hawaii

hi_dg_edits.py = Pickled dual graph that is used in HI_Markov_Chain_bl_adj.py and HI_Markov_Chain_bl_unadj.py. Must unzip file before running the pickle code.

hi_districtreallocation_returningdata_bg.csv = CSV file with adjusted and unadjusted population data at block group level in Hawaii. This is used in hawaii_final_gerry.py

hi_final_gerry.py  = Tests whether Arizona population data was properly imported into Python. Also fused Census block shapefile and population data to create az_merge.zip 

hi_merge.zip = Hawaii population shapefile used in HI_Markov_Chain_bl_adj.py and HI_Markov_Chain_bl_unadj.py

hi_shortbursts_results_aggregated_25.csv = File used to create boxplot for 25% Native Hawaiian/Pacific Islander

hi_shortbursts_results_aggregated_30.csv = File used to create boxplot for 30% Native Hawaiian/Pacific Islander

tl_2022_15_bg.zip  = Hawaii Census block group shapefile

tl_2022_15_tabblock20.zip = Hawaii Census block level shapefile
