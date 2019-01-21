import pandas as pd
import os

########################################################################################################################


def criteria_enforcer(card_df, criteria):
    """
    given pandas filtering criteria, will filter passed df and return the passed version
    :param card_df: a passed pandas dataframe, the returned version will be suitably filtered
    :param criteria: a series of 3 values  (column to filter on, operator, value to filter by)
    :return: a filtered pandas database
    """
    crt_attribute, crt_operator, crt_value = criteria  # split criteria into its 3 parts (attribute, operator, value)
    if crt_value.isnumeric():  # if the criteria value is a number but read as string
        crt_value = int(crt_value)  # convert to integer if needed (i.e. for ConvertedManaCost)

    if crt_operator == '=':
        card_df = card_df[card_df[crt_attribute] == crt_value]  # filter where attribute  ==   value
        return card_df
    elif crt_operator == '>':
        card_df = card_df[card_df[crt_attribute] > crt_value]  # filter where attribute  >   value
        return card_df
    elif crt_operator == '>=':
        card_df = card_df[card_df[crt_attribute] >= crt_value]  # filter where attribute  >=   value
        return card_df
    elif crt_operator == '<':
        card_df = card_df[card_df[crt_attribute] < crt_value]  # filter where attribute  <   value
        return card_df
    elif crt_operator == '<=':
        card_df = card_df[card_df[crt_attribute] <= crt_value]  # filter where attribute  <=   value
        return card_df
    elif crt_operator == '!=':
        card_df = card_df[card_df[crt_attribute] != crt_value]  # filter where attribute  !=   value
        return card_df


########################################################################################################################
criteria_files_path = '../3_benchmark_creation/benchmark_criteria_files/'  # relative path of script to criteria files
card_database_path = '../../2_database_creation/Card_Databases/'  # relative path to main db once directory changed
benchmark_database_path = '../benchmark_rebalance_files'  # relative path to directory where the benchmarks are saved
looping_criteria_path = '../benchmark_criteria_files/'  # because I'm folders change frequently need to restate for loop
mandatory_db_cols = ['uuid', 'mkm_url']  # columns always required from the parent db in child benchmark


os.chdir(criteria_files_path)  # folder of criteria files, 1 file per benchmark
criteria_files = [i for i in os.listdir(os.getcwd())]  # list of criteria files to be actioned in this script
database_name = [i for i in os.listdir(card_database_path) if '.csv' in i][0]  # filename of most recent card database


for crt_file in criteria_files:  # for every criteria file in the folder (i.e. for every benchmark to be created)
    os.chdir(looping_criteria_path)
    print(f'parsing "{crt_file}"')  # GUI
    df_criteria = pd.read_json(crt_file)  # read the criteria file into a json format
    mandatory_cols =  mandatory_db_cols + df_criteria[df_criteria.columns[0]].tolist()  # cols needed for benchmark file

    benchmark_df = pd.read_csv(card_database_path + database_name)[mandatory_cols]  # load card db with required cols
    for i in range(len(df_criteria.index)):  # for i in range(number of rows in the criteria file) i.e. for every row
        print(f'    parsing criteria {i+1}')  # GUI
        benchmark_df = criteria_enforcer(benchmark_df, df_criteria.loc[i])  # pass df and 'i'th fow of criteria file

    os.chdir(benchmark_database_path)  # change to where the rebalance file will be saved
    benchmark_file_name = crt_file.split('.')[0]+'.csv'  # save name is the same as the criteria file but .csv extension
    benchmark_df.to_csv(benchmark_file_name, index=False)  # write the benchmark database to a dynamic filename


# TODO : Test on larger scale for multiple filterings to ensure benchmark creation is consistent and reliable
