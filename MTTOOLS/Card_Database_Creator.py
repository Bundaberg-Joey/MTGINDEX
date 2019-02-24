import requests  # required to fetch the web pages containing the JSON formatted MTG set data
import json  # required to parse JSON data and convert to pandas readable form
from pandas.io.json import json_normalize  # used to easily convert the downloaded json data from mtgjson
import pandas as pd  # required to manipulate json and write to local file
from datetime import datetime  # used for writing the datetime stamp on the output file name
import os  # used in saving file to other folders
from collections import Counter  # used to version card names

########################################################################################################################


def set_df_builder(set_code, set_code_header):
    """
    Used to access the hosted json files, convert json format, read into a pandas dataframe and add the mtgjson_set_code
    as a column to the database for further parsing later on.
    :param set_code: the code used by mtgjson in their json URLs. Each code corresponds to one set
    :return: a pandas Dataframe containing all the card information for each set
    """
    page = requests.get(f'https://mtgjson.com/json/{set_code}.json')  # URL for json page
    set_cards_json = page.json()['cards']  # convert page to JSON and then read relevant section
    set_df = json_normalize(set_cards_json)  # normalize the JSON from the URL and write to pandas Dataframe
    set_df[set_code_header] = set_code  # add the mtgjson set code as a separate column to the dataframe
    return set_df


########################################################################################################################


def mkm_syntax_fixer(card_name):
    """
    Given the name of a card from MTGJSON, will update the string with the correct syntax for URL (i.e. " " --> "-")
    :param card_name: a string potentially containing string elements which need to be updated
    :return: a string where any string elements present in the below dictionary will have been converted to the fix
    """
    syntax_fixes = {" ": "-", ":": "", "'": "-", ".": "", ",": "", "--": "-"}  # dict of present:replacement
    for fix in syntax_fixes:  # for every punctuation key in the syntax list
        if fix in card_name:  # if this bit of punctuation is present
            card_name = card_name.replace(fix, syntax_fixes[fix])  # replace with the appropriate fix
    return card_name


########################################################################################################################


def card_name_corrector(card_names):
    """
    For multiple cards in the same MTG set, mkm will list them as different versions so need to update the card name
    The card name will also have any grammatical syntax updated as per the syntax fixer function
    :param card_names: a list/panda series of strings (in this instance card names)
    :return: a list of strings, list contains updated card version numbers and syntax if required
    """
    set_cards = Counter(card_names)  # take names from panda series and convert to Counter object
    duplicate_names = {card:set_cards[card] for card in set_cards if set_cards[card] != 1}  # only have unique entries

    corrected_card_names = []
    for card in card_names:  # so for every card name in the series of cards passed
        if card in duplicate_names and duplicate_names[card] != 0:  # if card has duplicates in set and the count != 0
            versioned_name = f'{card}-Version-{duplicate_names[card]}'  # create versioned card name
            corrected_card_names.append(mkm_syntax_fixer(versioned_name))  # update syntax & add to list to be returned
            duplicate_names[card] -=1  # update the counter dictionary
        else:
            corrected_card_names.append(mkm_syntax_fixer(card))  # catches unique cards & adds corrected names to list

    return corrected_card_names


########################################################################################################################

def database_info():
    """
    Creates a filename for the newly built file and also provides version number used in build
    :return: Tuple "(the file name used in the build, the full version number for updating the build version file)"
    """
    page = requests.get('https://mtgjson.com/json/version.json')
    version = json.loads(page.content)['version']  # takes mtgjson version from their website
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')  # generates time stamp for the database file
    build_name = 'MTCARD_{}_{}.csv'.format(version.replace(".", ""),timestamp)  # filename for new build
    return build_name, version


########################################################################################################################


def main():

    """Parses all json pages from mtgjson that have been mapped to sets in mkm. and creates pandas df for each one which
    is cleaned as required through syntax fixes. These smaller dfs are combined into a singular one which is then mapped
    and used to create URLs to the card's corresponding mkm page. This df is then saved to a csv and the local build
    version stored is updated.
    """
    h1, h2, h3, h4, h5 = ('mtgjson_set_code','name','mkm_name', 'mkm_web_name', 'mkm_map')  # cols referenced frequently

    mapping_df = pd.read_json('../../MTGINDEX/MTREFS/mapped_mtgjson_sets.json')  # mtgjson sets mapped to mkm
    set_code_list = mapping_df[h1]  # list of mtgjson set codes mapped to mkm

    df = pd.DataFrame()  # empty dataframe that will contain all collected mtgjson card sets
    for mtgjson_set in set_code_list:  # for every set code in the list of mapped sets
        print(f'Now processing {mtgjson_set}')  # GUI
        set_df = set_df_builder(mtgjson_set, h1)  # constructs the dataframe of each individual set, column name passed
        set_df[h3] = card_name_corrector(set_df[h2])  # create column containing names corrected for mkm
        df = df.append(set_df, sort=True)  # append the returned database to the main

    df = df.merge(mapping_df, on=h1)  # maps each set code to the set name used in the mkm URL
    url_prefix = '/en/Magic/Products/Singles/'  # used as prefix in all mkm URLs
    df[h5] = url_prefix + df[h4] + '/' + df[h3]  # mkm URL used to access any mapped mtg card

    database_name, build_version = database_info()  # unpack variables for file name and build version
    os.chdir('../../MTGINDEX/MTCARDS')  # change directory for saving file
    df.to_csv(database_name, index=False)  # save this data frame to appropriately named CSV file.

    with open('../../MTGINDEX/MTREFS/build_version.json', 'w') as f:  # used to update the stored build version
        f.write(json.dumps({"Build": build_version}))  # writes build version to the file


########################################################################################################################


if __name__ == '__main__':
    main()