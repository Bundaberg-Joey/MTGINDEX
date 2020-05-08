from mtgindex import utilities
from mtgindex.build import VersionController, AssembleSQL
from mtgindex.Allocation import ConstituentHandler
from mtgindex.Finance import BenchmarkHandler

if __name__ == '__main__':

    config = utilities.load_yaml('reference/config.yaml')

    mtgjson_loc = config['mtgjson_db_loc']
    mtcard_loc = config['mtcard_db_loc']
    mtbenchmark_loc = config['mtbenchmark_db_loc']

    print('version control')
    vc = VersionController()
    vc.fetch_current(location=config['local_version_path'])
    vc.fetch_queried(location=config['mtgjson_version_url'])

    if vc.compare_versions() is False:
        print('retrieving database')
        db = AssembleSQL.download_data(location=config['mtgjson_db_url'])
        print('building database')
        db.build(destination=mtgjson_loc)

    mtgjson_conn, mtcard_conn, mtbenchmark_conn = utilities.establish_connection(mtgjson_loc, mtcard_loc, mtbenchmark_loc)

    benchmark_queries = utilities.load_yaml(config['mtqueries_loc'])
    print('initialising handler')
    ch = ConstituentHandler(cons_origin=mtgjson_conn, cons_dest=mtcard_conn)
    bh = BenchmarkHandler(constituent_conn=mtcard_conn, benchmark_conn=mtbenchmark_conn)
    price_date = vc.format_pricedate(current='%Y-%m-%d', out='%Y-%m-%d')

    for benchmark in benchmark_queries:
        print('benchmark')
        query = benchmark_queries[benchmark]
        constituents = ch.select_cons(benchmark_query=query)

        if len(constituents) > 0:
            print('\t', 'Saving', benchmark)
            ch.save_cons(table=benchmark, constituents=constituents)
            # if table in benchmark level schema then calculate / append price
            # if not in benchmark table, create benchmark with new value

        else:
            print('\t', 'Dropping', benchmark)
            ch.drop_cons_table(table=benchmark)
            # if in benchmark table but not cons database then add nan value to benchmark for date

# TODO 1: Update so that price information is also retrieved with constituents. (don't break to much).
# TODO 2: Update index level with constituents.
# TODO 3: Store constituent level information.
