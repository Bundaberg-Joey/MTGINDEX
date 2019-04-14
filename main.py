import os
from MTTOOLS import Version_check
from MTTOOLS import TCG_Data_Scraper
from MTTOOLS import Card_Database_Creator

########################################################################################################################


def main():
    """
    MTGINDEX program file. Checks versions match and builds MTCARD database if versions do not match. Script then
    continues to scrape MKM in order to generate the daily MTDATA file. Also checks to see if a new set is listed on
    Mkm so I can update the mapping
    :return: No value returned, however MTDATA file generated daily and MTCARD file generated when required
    """

    os.chdir('MTTOOLS')  # change directory to allow MTTOOLS to function
    mtcard_versions_match = Version_check.main()  # Function checks if stored and online mtgjson versions match, bool

    if mtcard_versions_match == True:
        print(' >> MTGJSON and Build versions match, MTCARD rebuild not required')  # GUI
    elif mtcard_versions_match == False:
        print(' >> MTGJSON and Build versions out of sync, MTCARD rebuild required')  # GUI
        Card_Database_Creator.main()  # Generate a new MTCARD database file, only needed when mtgjson updates ~ monthly
        print('  >>> MTCARD File Built')  # GUI
    print(' >> Generating MTDATA')  # GUI
    TCG_Data_Scraper.main()  # Scrape mkm to get the daily UPEUR  and SHINV for listed cards, file saved to MTDATA
    print('  >>> MTDATA File Built')  # GUI


########################################################################################################################

if __name__ == '__main__':
    main()
