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



df_criteria = pd.read_json('../3_benchmark_creation/benchmark_criteria_files/2.json')  # criteria file
mandatory_cols = ['uuid', 'mkm_url'] + df_criteria['attribute'].tolist()  # list of required headers for rebalance db

df_database = pd.read_csv('../2_database_creation/Card_Databases/Card_Database_421_20190120_0949.csv')[mandatory_cols]  # main card db
print(df_database.shape)

for i in range(len(df_criteria.index)):  # for i in range(number of rows in the criteria file)
    df_database = criteria_enforcer(df_database, df_criteria.loc[i])
    print(df_database.shape)

# Can crudely do multiple filterings given operators.
# TODO 1) make this work for all criteria files (i.e. os and listdir and also loading the card DB multiple times 4 in 4
# TODO 2) Put an alert in so you know if result is a df.size == 0 (i.e. an empty database)
# TODO 3) Write each totally filtered df to a csv