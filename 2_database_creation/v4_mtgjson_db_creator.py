import requests  # required to fetch the web pages containing the JSON formatted MTG set data
import json  # required to parse through the JSON data and convert to python iterable values
import pandas as pd  # required to write the CSV file
from datetime import datetime  # used in filename versioning
import os  # used in saving file to other folders

########################################################################################################################


def card_dictionary_writer(set_code):
    """
    Converts online MTGJSON info on a passed set to a list of dictionaries, one dictionary per card in the set.
    :param set_code: 3 or 4 character code used by MTGJSON in naming their online json files, used to complete web URL
    :return: a list of python dictionaries where each list element is a dictionary and each dictionary is one cards info
    """
    json_set_dictionary = requests.get('https://mtgjson.com/json/'+set_code+'.json')
    python_set_dictionary = json.loads(json_set_dictionary.text)  # Convert JSON page to python dict

    set_card_dictionaries = []
    for card_dictionary in python_set_dictionary['cards']:  # only take 'cards' dict from downloaded json dictionary
        card_dictionary['mtgjson_set_code'] = set_code  # adds code of the set to the dictionary for later use
        set_card_dictionaries.append(card_dictionary)

    return set_card_dictionaries

########################################################################################################################


def card_array_writer(mtgjson_card_dict, mtgjson_attributes):
    """
    Converts list of dictionaries to a 2D array each sub array contains info for one card from mtgjson.
    :param mtgjson_card_dict: Passed dictionary containing one card's information
    :param mtgjson_attributes: List of dictionary keys expected to be present in this card dictionary
    :return: a 2D array where each sub array is the data from one card, N/A populated where card doesn't have key value
    """
    mtgjson_card_array = []  # to be array of all cards originally passed, each sub array = one card

    for i in range(0, len(mtgjson_card_dict)):  # dynamically scan the passed dict
        card_attribute_data = []  # this will be a sub list, each card will have a sub list which is appended to master
        for attribute in mtgjson_attributes:  # loops through card attribute list for each card dict passed
            if attribute in mtgjson_card_dict[i] and type(mtgjson_card_dict[i][attribute]) == 'unicode':
                card_attribute_data.append(mtgjson_card_dict[i][attribute].encode('ascii', 'ignore'))  # remove unicode for CSV
            elif attribute in mtgjson_card_dict[i]:  # takes the none unicode attributes (list and int)
                card_attribute_data.append(mtgjson_card_dict[i][attribute])  # writes non unicode to card array
            else:
                card_attribute_data.append("N/A")  # absent attributes (i.e. defense for an instant card)

        mtgjson_card_array.append(card_attribute_data)  # appends card's array to the main array

    return mtgjson_card_array


########################################################################################################################


def card_attribute_fetcher():
    """
    parses mtgjson online documentation to create a list of card attributes dynamically rather than stored in text file
    :return: list card attributes included in mtgjson doccumentation and those required for local database construction
    """
    page = requests.get('https://mtgjson.com/docs.html')  # page containing details about card documentation
    df = pd.read_html(page.content)[0]  # reads html into pandas array
    all_properties = df['Property'].tolist()  # saves column to list
    mtgjson_attributes = all_properties[1:all_properties.index('Token')]  # only keeps card specific attributes
    required_attributes = ['mtgjson_set_code']  # needed for construction of main database
    return mtgjson_attributes + required_attributes  # will return both of these concatenated


########################################################################################################################


def database_file_name():
    """
    Creates a filename for the newly built file, incorporating the current mtgjson version, date, and time the filename
    was minted. Sourced from webpage rather than stored text value to prevent miss match of versions.
    :return: name of file as a string
    """
    page = requests.get('https://mtgjson.com/json/version.json')
    mtgjson_version = json.loads(page.content)['version'].replace('.', '')  # takes mtgjson version from their website
    created_timestamp = datetime.now().strftime('%Y%m%d_%H%M')  # generates time stamp for the database file
    name_for_build = 'mtgjson_database_' + mtgjson_version + '_' + created_timestamp + '.csv'  # filename for new build
    return name_for_build


########################################################################################################################


def main():

    """Parses all json pages from mtgjson that have been mapped to sets in mkm.
    Creates a singular pandas database from these json files.
    Missing values placed as "N/A" within the database to prevent null values
    Writes db to csv."""

    path_to_set_mapping = 'v4_2_mapped_sets.csv'  # mtgjson and mkm have different sets so can't map cleanly between
    set_code_map = pd.read_csv(path_to_set_mapping)  # list of mapped codes

    list_of_mtgjson_card_dicts = []  # the list that individual card's dictionary will be added to for parsing in f
    for mtgjson_card_set in set_code_map['mtgjson_set_code']:  # for every set code in the list of mapped set codesset_code_map['mtgjson_set_code']:  # for every set code in the list of mapped set codes
        print('Starting set : ', mtgjson_card_set)  # GUI
        for mtgjson_sing_card_dict in card_dictionary_writer(mtgjson_card_set):  # for every card dict in the set list made
            list_of_mtgjson_card_dicts.append(mtgjson_sing_card_dict) # add to the master list used to create array later

    card_attributes = card_attribute_fetcher()  # List of available card attributes from mtgjson
    df = pd.DataFrame(card_array_writer(list_of_mtgjson_card_dicts, card_attributes),columns=card_attributes)
    os.chdir('../2_database_creation/mtgjson_databases')  # change directory for saving file
    df.to_csv(database_file_name(), index=False)  # save this data frame to appropriately named CSV file.


########################################################################################################################


if __name__ == '__main__':
    main()
