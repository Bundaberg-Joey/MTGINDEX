# TODO 1) loops through the criteria file directory and for each file in the directory it
# DONE 2) unpacks the criteria txt file into a series of nested lists to be read and manipulated into a pandas db
# DONE 3) the main db and criteria list are initially stripped of non filter columns to save memory in processing
# TODO 4) This smaller file is then recursively filtered according to criteria
# TODO 5) the fully filtered pandas db is then written to a csv file with the same name as criteria file
########################################################################################################################
import pandas as pd


df_criteria = pd.read_json('../3_benchmark_creation/benchmark_criteria_files/2.json')  # criteria file
mandatory_cols = ['uuid', 'mkm_url'] + df_criteria['property'].tolist()  # list of required headers for rebalance db

df_database = pd.read_csv('../2_database_creation/Card_Databases/Card_Database_421_20190120_0949.csv')[mandatory_cols]  # main card db
print(df_database.columns)

