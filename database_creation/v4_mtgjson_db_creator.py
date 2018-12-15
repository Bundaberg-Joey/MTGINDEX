import requests  # required to fetch the web pages containing the JSON formatted MTG set data
import json  # required to parse through the JSON data and convert to python iterable values
import pandas as pd  # required to write the CSV file
import datetime  # to be used in correctly versioning the master database csv file created
########################################################################################################################


def card_dictionary_writer(set_code):

    """Converts online JSON set info to a list of dictionaries, one dictionary per card in the set.
    Updated for mtgjson v4."""

    print('Starting     ', set_code)  # GUI
    json_set_dictionary = requests.get('https://mtgjson.com/v4/json/'+set_code+'.json')
    python_set_dictionary = json.loads(json_set_dictionary.text)  # Convert JSON page to python dict

    set_card_dictionaries = []
    for card_dictionary in python_set_dictionary['cards']:  # only take 'cards' dict from downloaded json dictionary
        card_dictionary['mtgjson_set_code'] = set_code  # adds code of the set to the dictionary for later use
        set_card_dictionaries.append(card_dictionary)

    print('Finished     ',set_code)  # GUI
    return set_card_dictionaries  # i.e. so return the list of dictionaries, for the set


########################################################################################################################


def card_array_writer(mtgjson_card_dict, mtgjson_attributes):

    """Converts list of dictionaries to a 2D array each sub array contains info for one card from mtgjson.
    Updated for mtgjson v4."""

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

    return mtgjson_card_array  # returns 2D array of lists


########################################################################################################################


def main():

    """Parses all json pages from mtgjson that have been mapped to sets in mkm.
    Creates a singular pandas database from these json files.
    Missing values placed as "N/A" within the database to prevent null values
    Writes db to csv."""

    path_to_set_mapping = 'C:/Users/Calum/PycharmProjects/MTG_INDEX_LEVELS/1_card_database/2_set_mapping/v4_2_mapped_sets.csv'
    set_code_map = pd.read_csv(path_to_set_mapping)  # codes

    list_of_mtgjson_card_dicts = []  # the list that individual card's dictionary will be added to for parsing in f
    for mtgjson_card_set in set_code_map['mtgjson_set_code']:  # for every set code in the list of mapped set codes
        for mtgjson_sing_card_dict in card_dictionary_writer(mtgjson_card_set):  # for every card dict in the set list made
            list_of_mtgjson_card_dicts.append(mtgjson_sing_card_dict) # add to the master list used to create array later

    with open('v4_mtgjson_card_properties.txt', 'r') as f:
        card_attributes = [line.rstrip() for line in f.readlines()]  # List of available card attributes from mtgjson
    df = pd.DataFrame(card_array_writer(list_of_mtgjson_card_dicts, card_attributes),columns=card_attributes)

    created_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')  # generates time stamp for the database file
    version = 'C:/Users/Calum/PycharmProjects/MTG_INDEX_LEVELS/1_card_database/1_mtgjson_update_check/version_check.txt'
    with open(version,'r') as f:
        build_version = (f.readlines()[1].split(' ')[1].rstrip()).replace('.', '')  # current mtgjson online version
    database_file_name = "mtgjson_database_" + build_version + "_" + created_timestamp + ".csv"

    df.to_csv(database_file_name, index=False)  # save this data frame to appropriately named CSV file.


########################################################################################################################


if __name__ == '__main__':
    main()
