import os
from MTTOOLS import Version_check
from MTTOOLS import Benchmark_Level_Aggregator
from MTTOOLS import Card_Database_Creator
from MTTOOLS import Benchmark_Builder

########################################################################################################################


def main():
    """
    MTGINDEX program file.
    Checks if the local price version matches the one hosted on MTGJSON. if thee dates do not match then rebalances:

    Rebalance:
                1) The MTCARD file is recreated from MTGJSON, this master cons file is used to rebalance benchmarks
                2) The benchmarks are rebuilt based on the new MTCARD file
                3) The rebalanced cons files have their index levels calculated for the dates in the recent MTCARD

    """

    os.chdir('MTTOOLS')  # change directory to allow MTTOOLS to function
    if Version_check.main() == True:
        print(' >> MTGJSON and Local Price versions match, rebalance not required')
    else:
        print(' >> Difference in MTGJSON and Local price versions\n  >> Rebuilding MTCARD')
        Card_Database_Creator.main()  # Generate a new MTCARD database file including the price data
        print(' >> MTCARD File Built \n  >> Rebalancing Benchmarks (writing MTCONS files)')
        Benchmark_Builder.main()  # filter master cons database to create constituent listings including prices
        print(' >> Benchmarks Rebalanced \n  >> Generating MTINDEX File')
        Benchmark_Level_Aggregator.main()  # Parse benchmark constituent files to calculate weekly index levels
        print(' >> MTINDEX File Built')


########################################################################################################################

if __name__ == '__main__':
    main()
