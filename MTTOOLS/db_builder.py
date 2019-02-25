import os
import pandas as pd
folder_path = '../../MTGINDEX/MTDATA'

os.chdir(folder_path)
file_list = [i for i in os.listdir(os.getcwd())]  # list of files

old_df = pd.read_csv(file_list[1])  # first file
cons_df = pd.read_csv(file_list[2])  # second file


prior_db_maps = old_df['mkm_map'].tolist()  # convert to lists
daily_cons = cons_df['mkm_map'].tolist()


all_maps = prior_db_maps + ([i for i in daily_cons if i not in prior_db_maps])  # create updated list of columns (i.e. add new ones to list)


updated_df = pd.DataFrame({'mkm_map':all_maps})  # create new db with those columns

new = pd.merge(updated_df, old_df, on='mkm_map', how='left')  # merge on left to keep new rows

new2 = pd.merge(new, cons_df, on='mkm_map', how='left')  # merge on left to keep shape

new2.to_csv('ladies_and_gentlmen.csv')