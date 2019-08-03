import os
import pandas as pd
import numpy as np
from datetime import datetime

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

def benchmark_level_aggregator(price_columns, benchmark_files, file_path):
    """
    Given all dates and benchmark files, calculates the index level of each benchmark on each date and stores in a
    Pandas.DataFrame

    :param price_columns: list, used to iterate through benchmark dfs
    :param benchmark_files: list, all csv benchmark files to be parsed, benchmark name extracted from filename
    :param file_path: str, location of directory containing the benchmark files which  will be parsed

    :return: Pandas.DataFrame, calculated index levels, cols=dates, index=benchmarks
    """
    dates = [i.split('.')[-1] for i in price_columns]  # use date only as mtgjson changes keys frequently
    benchmark_names = [i.replace('MTCONS_','').replace('.csv', '') for i in benchmark_files]
    #extact benchmark name from benchmark file

    df = pd.DataFrame(columns=dates, index=benchmark_names)  # preallocate memory for the df

    for name, benchmark in zip(benchmark_names, benchmark_files):
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
    The index levels are then saved to a Pandas DataFrame which is written to a csv file
    """
    mtgindex_loc = {'MTBENCHMARKS':'../MTBENCHMARKS/', 'save_to':'../MTINDEX/'}
    mtgjson_keys = ['prices.paper.']  # fields used by mtgjson, prone to renaming
    benchmark_folder, save_folder = mtgindex_loc['MTBENCHMARKS'], mtgindex_loc['save_to']

    benchmark_files = [f for f in os.listdir(benchmark_folder) if '.csv' in f]  # benchmark csv files
    generic_headers = pd.read_csv(F"{benchmark_folder}{benchmark_files[0]}").columns # get headers from benchmark file
    price_columns = [col for col in generic_headers if mtgjson_keys[0] in col]  # extract relevant price column headers

    timestamp = datetime.now().strftime('%Y%m%d')  # generates time stamp for the files
    all_benchmark_levels = benchmark_level_aggregator(price_columns=price_columns, benchmark_files=benchmark_files, file_path=benchmark_folder)
    all_benchmark_levels.to_csv(F"{save_folder}Index_Values_{timestamp}.csv")
    #all_benchmark_changes = all_benchmark_levels.pct_change(axis='columns')  # calculates percentage changes along rows
    #all_benchmark_changes.to_csv(F"{save_folder}Index_Changes_{timestamp}.csv")  # keep for later development


########################################################################################################################

if __name__ == '__main__':
    main()
