import pandas as pd
import numpy as np
import datetime
import os
import json

########################################################################################################################


def cons_date_finder(index_t_1):
    """
    Given the index date (t-1), return the two strings needed to access constituent prices on (t) and (t-1)

    :param index_t_1: str, date in the format '%d/%m/%Y'

    :return: (str, str, str), the three keys needed to access cons data for day (t) and day (t-1) and index data (t)
    """
    date_t_1 = datetime.datetime.strptime(index_t_1, '%d/%m/%Y')
    date_t = date_t_1 + datetime.timedelta(days=7)
    t_1_cons = datetime.datetime.strftime(date_t_1, '%Y-%m-%d')
    t_cons = datetime.datetime.strftime(date_t, '%Y-%m-%d')
    t_index = datetime.datetime.strftime(date_t, '%d/%m/%Y')
    return t_1_cons, t_cons, t_index


########################################################################################################################


def benchmark_level(cons, t_1_index, t, t_1):
    """
    Calculates the new benchmark value of day (t) based on the below formula, where all constituents are assumed to
    have an equally weighted contribution to the index in the absence of nominal outstanding data

    benchmark_value(t) = benchmark_value(t-1) * (1 + sum(constituent_returns(t))

    :param cons: Pandas.DataFrame, constituent benchmark file containing required prices of constituents per benchmark
    :param t_1_index: float, benchmark value from previous day (t-1)
    :param t: str, key to access the prices of the constituents in the passed df from day (1)
    :param t_1: str, key to access the prices of the constituents in the passed df from day (t-1)

    :return: float, calculated benchmark value for day (t)
    """
    cons = cons[[t_1, t]]  # focus down cons to day (t) and (t-1)
    cons_returns = cons.pct_change(axis='columns')[t]  # calcs return of the cons, slices for relevant column after
    t_index = t_1_index * (1 + np.sum(cons_returns))
    return  t_index


########################################################################################################################


def constituent_data_available(path_to_cons, cons_file, cons_date_t):
    """
    To prevent issues with calculations occurring when data is not yet available for the required date, this function
    checks a constituent file to see if day (t) is present as a header. If yes then the function returns True allowing
    the main script to continue. As all constituent files are filtered versions of the master cons file, a column in
    one will be present in all, hence only the first file has to be checked

    :param path_to_cons: str, path to the directory containing the benchmark constituent files
    :param cons_file: str, name of a constituent file to be checked for date inclusion
    :param cons_date_t: str, the date to check if included or not

    :return: Bool, True if the date does exist and the data is available to calculate the benchmark levels, else False
    """
    constituent_columns = pd.read_csv(F"{path_to_cons}{cons_file}").columns
    date_check = sum([1 for col in constituent_columns if cons_date_t in col])
    return True if date_check > 0 else False


########################################################################################################################


def all_benchmark_levels(master_index_df, cons_path, benchmark_names, cons_files, dates, column_key):
    """
    Iterates though all available constituent level files and calculates the benchmark values for those benchmarks for
    the dates passed. The benchmark levels are added to a Pandas.DataFrame which is eventually returned and incorporated
    into the main data structure. If a benchmark's name is not in the original file (i.e. it is a new benchmark due
    to their being a new type available from a release), then a new benchmark entry will be created, valued at 1000,
    allowing for an updated value to be calculated next time

    :param master_index_df: Pandas.DataFrame, contains all prior index level values
    :param cons_path: str, path to directory containing constituent benchmark files
    :param benchmark_names: list, benchmark names as saved in the master file index, used to recreate df that's returned
    :param cons_files: list, names of all benchmark files to be passed to pandas open_csv
    :param dates: list, all index and constituent dates for (t) and (t-1) to be used when accessing price / index data
    :param column_key: str, mtgjson column string component used to mark required price columns, prone to change

    :return: df: Pandas.DataFrame, all calculated benchmark values for day (t)
    """

    t_1_index, t_cons, t_1_cons, t_index = dates  # unpack dates into single variables
    df = pd.DataFrame(index=benchmark_names, columns=[t_index])

    for name, benchmark_file in zip(benchmark_names, cons_files):
        benchmark_cons_df = pd.read_csv(F'{cons_path}{benchmark_file}')  # load cons file
        if name not in master_index_df.index:
            df.loc[name] = 1000  # if new benchmark then set level as 1000
        else:
            level_index_t_1 = master_index_df[t_1_index].loc[name]  # index_level of (t-1)
            benchmark_cons_df.columns = [i.replace(column_key, '') for i in benchmark_cons_df.columns]  # only dates
            df.loc[name] = benchmark_level(cons=benchmark_cons_df, t_1_index=level_index_t_1, t=t_cons, t_1=t_1_cons)
            # calculate index level for the benchmark
    return df


########################################################################################################################


def main():
    """
    Calculates the benchmark levels for all available benchmarks for day (t) and updates the main benchmark file:

    1) The main benchmark file is loaded and from there, the next data dates to be assessed are determined
    2) A check is made to see if constituent data is available for the date to be calculated, if not then exits main()
    3) If True, then all benchmark values are calculated iteratively so long as a constituent file exists for it
    4) The main index file is then concatenated with the values for day (t)
    5) The benchmark returns are calculated from the updated benchmark file
    6) Both benchmark levels and returns DataFrames are saved to csv files, overwriting previous file contents
    ** NOTE : These files are backed up routinely and so long as cons data is available they can be recreated easily

    :return: Bool, True if benchmark levels calculated for day (t), False if cons information not available for (t)
    """
    mtgindex_loc = {'Master_Index': '../MTINDEX/MTINDEX_Values.csv',
                    'Master_Returns': '../MTINDEX/MTINDEX_Returns.csv',
                    'Constituent_Folder': '../MTBENCHMARKS/',
                    'save_to': '../MTINDEX/',
                    'Version_File':'../MTREFS/price_version.json'}

    mtgjson_keys = ['prices.paper.']

    master_index_df = pd.read_csv(mtgindex_loc['Master_Index'], index_col=0)  # master index record file for t-1 val
    t_1_index = master_index_df.columns[-1]  # extract most recent benchmark value date
    t_1_cons, t_cons, t_index = cons_date_finder(t_1_index)  # determines dates (t-1) and (t) for cons & index levels

    cons_files = [f for f in os.listdir(mtgindex_loc['Constituent_Folder']) if '.csv' in f]  # list of benchmark csv

    if constituent_data_available(mtgindex_loc['Constituent_Folder'], cons_files[0], t_cons):  # Sanity check
        benchmark_names = [i.split('_')[-1].split('.')[0] for i in cons_files] # used to locate index in master df

        day_t_index_values = all_benchmark_levels(master_index_df=master_index_df,
                                           cons_path=mtgindex_loc['Constituent_Folder'],
                                           benchmark_names=benchmark_names,
                                           cons_files=cons_files,
                                           dates=[t_1_index, t_cons, t_1_cons, t_index],
                                           column_key=mtgjson_keys[0])  # calculate all benchmark values for day (t)

        updated_master_levels = pd.concat([master_index_df, day_t_index_values], axis=1, sort=True)  # update master
        updated_master_returns = updated_master_levels.pct_change(axis='columns')  # calculate benchmark level returns

        updated_master_levels.to_csv(F"{mtgindex_loc['save_to']}{mtgindex_loc['Master_Index']}")  # save files
        updated_master_returns.to_csv(F"{mtgindex_loc['save_to']}{mtgindex_loc['Master_Returns']}")

        with open(mtgindex_loc['Version_File'], 'w') as f:  # Update the stored Price version
            f.write(json.dumps({"Price_Build": t_cons}))

        print(F' >>> Completed for date {t_index}')  # GUI
        return True
    else:
        print(F' >>> No constituent data available for {t_index}, currently up to date')  # GUI
        return False


########################################################################################################################

if __name__ == '__main__':
    while True:  # in case multiple weeks are missed by user, this way script loops till benchmarks all up to date
        if main() == False:
            break
