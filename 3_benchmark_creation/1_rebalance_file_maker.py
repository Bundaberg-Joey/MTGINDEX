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
        card_df = card_df[card_df[crt_attribute] > crt_value]  # filter where attribute  ==   value
        return card_df
    elif crt_operator == '>=':
        card_df = card_df[card_df[crt_attribute] >= crt_value]  # filter where attribute  ==   value
        return card_df
    elif crt_operator == '<':
        card_df = card_df[card_df[crt_attribute] < crt_value]  # filter where attribute  ==   value
        return card_df
    elif crt_operator == '<=':
        card_df = card_df[card_df[crt_attribute] <= crt_value]  # filter where attribute  ==   value
        return card_df
    elif crt_operator == '!=':
        card_df = card_df[card_df[crt_attribute] != crt_value]  # filter where attribute  ==   value
        return card_df


########################################################################################################################
os.chdir('../3_benchmark_creation/benchmark_criteria_files')  # folder of criteria files, 1 file per benchmark
criteria_files = [i for i in os.listdir(os.getcwd())]  # list of criteria files

for crt_file in criteria_files:  # for every criteria file in the folder
    df_criteria = pd.read_json(crt_file)  # read the file into a json format
    mandatory_cols = ['uuid', 'mkm_url'] + df_criteria['attribute'].tolist()  # list of required headers for rebalance db

    df_database = pd.read_csv('../../2_database_creation/Card_Databases/Card_Database_421_20190120_0949.csv')[mandatory_cols]  # main card db

    for i in range(len(df_criteria.index)):  # for i in range(number of rows in the criteria file)
        df_database = criteria_enforcer(df_database, df_criteria.loc[i])  # pass dataframe and ith fow of criteria file
        if df_database.size == 0:  # check to see if resultant database is empty
            print('The filtered database is empty')  # GUI

    os.chdir('../benchmark_rebalance_files')  # change to where the rebalance file will be saved
    df_database.to_csv('thingy.csv', index=False)  # write the file to a name

# Can crudely do multiple filterings given operators.
# TODO 3) Write each totally filtered df to a csv with appropriate name
# TODO 4) needs to take most recent card database file as input also as currently hardcoded for just the one
