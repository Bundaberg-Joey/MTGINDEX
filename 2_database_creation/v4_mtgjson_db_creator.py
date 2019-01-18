import requests  # required to fetch the web pages containing the JSON formatted MTG set data
import json  # required to parse JSON data and convert to pandas readable form
from pandas.io.json import json_normalize  # used to easily convert the downloaded json data
import pandas as pd  # required to manipulate json and write to local file
from datetime import datetime  # used for writing the datetime stamp on the output file name
import os  # used in saving file to other folders

########################################################################################################################


def card_df_builder(set_code):
    """
    Used to access the hosted json files, convert json format, read into a pandas dataframe and add the mtgjson_set_code
    as a column to the database for further parsing later on.
    :param set_code: the code used by mtgjson in their json URLs. Each code corresponds to one set
    :return: a pandas Dataframe containing all the card information for each set
    """
    page = requests.get('https://mtgjson.com/json/{}.json'.format(set_code))  # URL for json page
    set_cards_json = json.loads(page.content)['cards']  # convert page to JSON and then read relevant section
    set_df = json_normalize(set_cards_json)  # normalize the JSON from the URL and write to pandas Dataframe
    set_df['mtgjson_set_code'] = set_code  # add the mtgjson set code as a separate column to the dataframe
    return set_df


########################################################################################################################


def database_file_name():
    """
    Creates a filename for the newly built file, incorporating the current mtgjson version, date, and time the filename
    was minted. Sourced from web page rather than stored text value to prevent miss match of versions.
    :return: name of file as a string
    """
    page = requests.get('https://mtgjson.com/json/version.json')
    version = json.loads(page.content)['version'].replace('.', '')  # takes mtgjson version from their website
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')  # generates time stamp for the database file
    name_for_build = f'mtgjson_database_{version}_{timestamp}.csv'  # filename for new build
    return name_for_build


########################################################################################################################


def main():

    """Parses all json pages from mtgjson that have been mapped to sets in mkm.
    Creates a singular pandas database from these json files.
    Missing values placed as "N/A" within the database to prevent null values
    Writes db to csv."""

    mapping_file = 'v4_mapped_sets.json'  # file of mtgjson sets that have been mapped to mkm
    set_code_map = pd.read_json(mapping_file)['mtgjson_set_code']  # list of mapped codes

    df = pd.DataFrame()
    for mtgjson_set in set_code_map:
        print(f'Now parsing {mtgjson_set}')
        df = df.append(card_df_builder(mtgjson_set), sort=True)

    os.chdir('../2_database_creation/mtgjson_databases')  # change directory for saving file
    df.to_csv(database_file_name(), index=False)  # save this data frame to appropriately named CSV file.


########################################################################################################################


if __name__ == '__main__':
    main()
