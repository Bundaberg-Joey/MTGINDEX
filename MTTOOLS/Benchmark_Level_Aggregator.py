import os
import pandas as pd
import numpy as np
from datetime import datetime
import json

########################################################################################################################


def benchmark_level(index_date):
    """
    Calculates the price weighted index of the benchmark for a given day, due to some prices missing from mtgjson,
    np.nan is used to prevent a divisor by zero occurring and results in there being no index value for that day

    :param index_date: Pandas.Series, the individual card prices of a benchmark's constituents on a given day

    :return: float, the price weighted benchmark level or np.nan if no valid constituents for that day
    """
    priced_entries = index_date.dropna()
    index_sum, index_divisor= sum(priced_entries), len(priced_entries)
    if index_divisor > 0:
        index_value = index_sum / index_divisor
    else:
        index_value = np.nan
    return index_value


########################################################################################################################

def benchmark_level_aggregator(price_columns, cons_files, file_path):
    """
    Given all dates and benchmark files, calculates the index level of each benchmark on each date and stores in a
    Pandas.DataFrame

    :param price_columns: list, used to iterate through benchmark dfs
    :param cons_files: list, all csv benchmark files to be parsed, benchmark name extracted from filename
    :param file_path: str, location of directory containing the benchmark files which  will be parsed

    :return: Pandas.DataFrame, calculated index levels, cols=dates, index=benchmarks
    """
    dates = [i.split('.')[-1] for i in price_columns]  # use date only as mtgjson changes keys frequently
    benchmark_names = [i.replace('MTCONS_','').replace('.csv', '') for i in cons_files]
    #extact benchmark name from benchmark file

    df = pd.DataFrame(columns=dates, index=benchmark_names)  # preallocate memory for the df

    for name, benchmark in zip(benchmark_names, cons_files):
        benchmark_levels = []
        benchmark_df = pd.read_csv(F'{file_path}{benchmark}')
        for date in price_columns:
            benchmark_levels.append(benchmark_level(benchmark_df[date]))
        df.loc[name] = benchmark_levels

    return df

########################################################################################################################

def main():
    """
    Parses all constituent files for the benchmarks to extract the price data and calculate the index levels for them.
    The index levels are then saved to a Pandas DataFrame which is then joined onto the master index level dataframe.
    The returns are then calculated from the master file and then save to the main returns file.
    Both original index levels and index returns are overwritten each time the script executes
    """
    timestamp = datetime.now().strftime('%Y%m%d')  # generates time stamp for the files

    mtgindex_loc = {'MTBENCHMARKS':'../MTBENCHMARKS/',  # saves changing paths in the main script
                    'save_to':'../MTINDEX/',
                    'Index_Levels_Master':'../Index_Values.csv',
                    'Index_Returns_Master':'../Index_Returns.csv'}

    benchmark_folder, save_folder = mtgindex_loc['MTBENCHMARKS'], mtgindex_loc['save_to']
    mtgjson_keys = ['prices.paper.']  # fields used by mtgjson, prone to renaming

    cons_files = [f for f in os.listdir(benchmark_folder) if '.csv' in f]  # benchmark csv files
    generic_headers = pd.read_csv(F"{benchmark_folder}{cons_files[0]}").columns # get headers from benchmark file
    dates = [col for col in generic_headers if mtgjson_keys[0] in col]  # extract relevant price column headers

    mtgjson_levels = benchmark_level_aggregator(price_columns=dates, cons_files=cons_files, file_path=benchmark_folder)

    master_index_levels = pd.read_csv(mtgindex_loc['Index_Levels_Master'], index_col=0)  # read master index file
    updated_master_levels = pd.concat([master_index_levels, mtgjson_levels], axis=1, sort=True)  # update with recent
    updated_master_returns = updated_master_levels.pct_change(axis='columns')  # calculate returns

    mtgjson_levels.to_csv(F"{save_folder}Index_Values_{timestamp}.csv")  # store for historical reference
    updated_master_levels.to_csv(mtgindex_loc['Index_Levels_Master'])  # overwrite existing  with  updated
    updated_master_returns.to_csv(mtgindex_loc['Index_Returns_Master'])  #  overwrite existing  with  updated

    with open('../MTREFS/price_version.json', 'w') as f:  # used to update the stored Price version
        f.write(json.dumps({"Price_Build": mtgjson_levels.columns[-1]}))

########################################################################################################################

if __name__ == '__main__':
    main()
