from mtgindex import utilities
from mtgindex.build import VersionControl, AssembleSQL
from mtgindex.pipeline import ConstituentPipeline, BenchmarkPipeline

if __name__ == '__main__':

    config = utilities.load_yaml('reference/config.yaml')

    mtgjson_loc = config['mtgjson_db_loc']
    mtcard_loc = config['mtcard_db_loc']
    mtbenchmark_loc = config['mtbenchmark_db_loc']

    print('version control')
    vc = VersionControl()
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
    ch = ConstituentPipeline(cons_origin=mtgjson_conn, cons_dest=mtcard_conn)
    bh = BenchmarkPipeline(constituent_conn=mtcard_conn, benchmark_conn=mtbenchmark_conn)
    price_date = vc.format_pricedate(current='%Y-%m-%d', out='%Y-%m-%d')

    for benchmark in benchmark_queries:
        query = benchmark_queries[benchmark]
        constituents = ch.select_cons(benchmark_query=query)

        if len(constituents) > 0:
            print('\t', 'Saving', benchmark)
            # get prices of these constituents
            # if benchmark already exists:
            #   save prices to column in a list
            #   calculate index levl
            #   save index level adjacent column to cons prices
            # else:
            #   create new table
            #   save prices to column in list
            #   add starter index value

            ch.save_cons(table=benchmark, constituents=constituents)  # save the constituents to a file for future ref

        else:
            print('\t', 'Dropping', benchmark)
            ch.drop_cons_table(table=benchmark)
            # if benchmark already exists:
            #   propagate index value with NaN or other such value
            #   update cons data to be empty list for that day
            # else:
            #   create new table
            #   save empty list of cons prices
            #   save Nan or other such value as index level

# TODO 1 : Add logger class to track ongoing process
# TODO 2 : Create index levels from constituents
# TODO 3 : Store constituent level price information
