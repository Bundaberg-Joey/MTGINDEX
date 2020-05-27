import sqlite3

from mtgindex import utilities
from mtgindex.build import VersionControl, AssembleSQL
from mtgindex.benchmark import PriceWeightedBenchmark
from mtgindex.database import MtgIndex

if __name__ == '__main__':

    mtgjson_loc = 'database/mtgjson.sqlite'
    mtgindex_loc = 'database/mtgindex.sqlite'

    print('version control')
    vc = VersionControl()
    vc.fetch_current(location='reference/local_price_date.txt')
    vc.fetch_queried(location='https://mtgjson.com/json/version.json')

    if vc.compare_versions() is False:
        db = AssembleSQL.download_data('https://www.mtgjson.com/files/AllPrintings.sqlite')
        db.build(destination=mtgjson_loc)

    index_queries = utilities.load_yaml('reference/mtqueries.yml')
    price_date = '2020-05-24'  #vc.format_pricedate(current='%Y-%m-%d', out='%Y-%m-%d')
    # hard code date for initial testing

    conn = sqlite3.connect(mtgjson_loc)
    curr = conn.cursor()

    mtg = MtgIndex(mtgindex_loc)  # create object to interact with main database

    for index_name in index_queries:
        print(index_name)
        criteria = index_queries[index_name]
        benchmark = PriceWeightedBenchmark(name=index_name, criteria=criteria, evaluation_type='paper', evaluation_date=price_date)
        benchmark.apply_criteria(curr)
        benchmark.evaluate_constituents(curr)

        if mtg.table_exist(index_name):
            print('\t', 'updating mtgindex table')
            benchmark.get_prior_index(mtgindex_curr=mtg.curr)  # retrieve prior index value for calculation
            benchmark.weight_constituents()  # caluculate index level
            benchmark.calculate_index_level()
            mtg.update_benchmark_table(benchmark)
        else:
            mtg.add_benchmark(benchmark)
            print('\t', 'creating mtgindex table')
            benchmark.get_prior_index(mtgindex_curr=mtg.curr)  # retrieve prior index value for calculation
            benchmark.index_value = 1000.0
            mtg.update_benchmark_table(benchmark)

    # TODO : Set the index value to be 1000.0 using the benchmark class rather than through hard coding
    # TODO : Have tested the benchmark and can create index values for 2020-05-24 but need to see about how to update the values for new dates
    # TODO 2: For each benchmark, see which dates exist in mtgindex and then evaluate for any FUTURE price dates present which are not in mtgindex
    # FUTURE prices need to be used to avoid adding in new index values which are prior information which just fucks the whole thing!!
