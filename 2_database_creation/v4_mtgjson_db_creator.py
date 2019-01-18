import requests  # required to fetch the web pages containing the JSON formatted MTG set data
import json  # required to parse JSON data and convert to pandas readable form
from pandas.io.json import json_normalize  # used to easily convert the downloaded json data
import pandas as pd  # required to manipulate json and write to local file
from datetime import datetime  # used for writing the datetime stamp on the output file name
import os  # used in saving file to other folders

########################################################################################################################


def set_df_builder(set_code, set_code_header):
    """
    Used to access the hosted json files, convert json format, read into a pandas dataframe and add the mtgjson_set_code
    as a column to the database for further parsing later on.
    :param set_code: the code used by mtgjson in their json URLs. Each code corresponds to one set
    :return: a pandas Dataframe containing all the card information for each set
    """
    page = requests.get('https://mtgjson.com/json/{}.json'.format(set_code))  # URL for json page
    set_cards_json = json.loads(page.content)['cards']  # convert page to JSON and then read relevant section
    set_df = json_normalize(set_cards_json)  # normalize the JSON from the URL and write to pandas Dataframe
    set_df[set_code_header] = set_code  # add the mtgjson set code as a separate column to the dataframe
    return set_df


########################################################################################################################


def database_info():
    """
    Creates a filename for the newly built file and also provides version number used in build
    :return: Tuple "(the file name used in the build, the full version number for updating the build version file)"
    """
    page = requests.get('https://mtgjson.com/json/version.json')
    version = json.loads(page.content)['version']  # takes mtgjson version from their website
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')  # generates time stamp for the database file
    build_name = f'mtgjson_database_{version.replace(".", "")}_{timestamp}.csv'  # filename for new build
    return build_name, version


########################################################################################################################


def main():

    """Parses all json pages from mtgjson that have been mapped to sets in mkm.
    Creates a singular pandas database from these json files.
    Missing values placed as "N/A" within the database to prevent null values
    Writes db to csv."""

    mapping_file = 'v4_mapped_sets.json'  # file of mtgjson sets that have been mapped to mkm
    set_code_map = pd.read_json(mapping_file)['mtgjson_set_code']  # list of mapped codes

    df = pd.DataFrame()  # empty dataframe that will contain all collected mtgjson card sets
    for mtgjson_set in set_code_map:  # for every set code in the list of mapped sets
        print(f'Now parsing {mtgjson_set}')  # GUI
        df = df.append(set_df_builder(mtgjson_set, 'mtgjson_set_code'), sort=True)  # append the returned database main

    database_name, build_version = database_info()
    os.chdir('../2_database_creation/mtgjson_databases')  # change directory for saving file
    df.to_csv(database_name, index=False)  # save this data frame to appropriately named CSV file.

    with open('../../1_update_check/build_version.json', 'w') as f:  # used to update the stored build version
        f.write(json.dumps({"Build": build_version}, indent=4))  # writes build version to the file


########################################################################################################################


if __name__ == '__main__':
    main()
