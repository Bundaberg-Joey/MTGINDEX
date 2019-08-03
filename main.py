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
    mtcard_versions_match = Version_check.main()  # Function checks if stored and online mtgjson versions match, bool

    if mtcard_versions_match == True:
        print(' >> MTGJSON and Local Price versions match, rebalance not required')  # GUI
    else:
        print(' >> Difference in MTGJSON and Local versions, rebuild required')
        print(' >> Rebuilding MTCARD, master constituents file')  # GUI
        Card_Database_Creator.main()  # Generate a new MTCARD database file, only needed when mtgjson updates ~ monthly
        print(' >> MTCARD File Built')  # GUI
        print(' >> Rebalancing Benchmarks (writing MTCONS files)')  # GUI
        Benchmark_Builder.main()
        print(' >> Benchmarks Rebalanced')
        print(' >> Generating MTINDEX File')  # GUI
        Benchmark_Level_Aggregator.main()  # Scrape mkm to get the daily UPEUR  and SHINV for listed cards, file saved to MTINDEX
        print(' >> MTINDEX File Built')  # GUI


########################################################################################################################

if __name__ == '__main__':
    main()
