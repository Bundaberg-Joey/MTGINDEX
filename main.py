import sqlite3

from mtgindex import utilities
from mtgindex.build import VersionControl, AssembleSQL
from mtgindex.benchmark import PriceWeightedBenchmark

if __name__ == '__main__':

    mtgjson_loc = 'database/mtgjson.sqlite'
    mtgindex_loc = 'database/mtgindex.sqlite'

    print('version control')
    vc = VersionControl()
    vc.fetch_current(location='reference/local_price_date.txt')
    vc.fetch_queried(location='https://mtgjson.com/json/version.json')

    if vc.compare_versions() is False:
        print('retrieving database')
        db = AssembleSQL.download_data('https://www.mtgjson.com/files/AllPrintings.sqlite')
        print('building database')
        db.build(destination=mtgjson_loc)

    index_queries = utilities.load_yaml('reference/mtqueries.yml')
    price_date = vc.format_pricedate(current='%Y-%m-%d', out='%Y-%m-%d')

    conn = sqlite3.connect(mtgjson_loc)
    curr = conn.cursor()

    for index_name in index_queries:
        print(index_name)
        criteria = index_queries[index_name]
        benchmark = PriceWeightedBenchmark(name=index_name, criteria=criteria, evaluation_type='paper', evaluation_date=price_date)
        benchmark.apply_criteria(curr)
        benchmark.evaluate_constituents(curr)

    # TODO 1: Test that the PriceWeightedBenchmark class works like it's meant to!!!
    # TODO 2: Once fully integrated, create yaml file which tracks dates which have been assessed
    # TODO 3: develop a function which can see which dates have not been assessed from MTGJSON database so can iterate through them
