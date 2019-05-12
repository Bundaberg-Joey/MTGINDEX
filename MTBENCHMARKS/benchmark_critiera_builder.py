import pandas as pd
import json
import os
import requests

########################################################################################################################


def mtcard_file(path_to_mtcards):
    """
    Because new MTCARD files will be created whenever mtgjson updates, providing the location of the mtcard files allows
    for dynamic loading of the most recent mtgjson file, regardless of name.
    :param path_to_mtcards: relative path to the MTCARDS folder
    :return Pandas.DataFrame of the latest mtcard file
    """
    mtcard_name = os.listdir(path_to_mtcards)[-1]
    mtcard_df = pd.read_csv(path_to_mtcards+mtcard_name, dtype='str')
    mtcard_df['text'] = mtcard_df['text'].str.lower()
    return mtcard_df


########################################################################################################################


def mtcard_types(mtgjson_url):
    """
    very difficult to reconstruct the list of of subtypes from the MTCARD file so have rebuilt it from the hosted
    json file by MTGJSON instead. Due to mtgjson parsing, need to flatten nested lists.
    :param mtgjson_url: url address of the hosted subtypes
    :return mtgjson_subtypes: 1D list, entry of every single subtype extracted from mtgjson
    """
    page = requests.get(mtgjson_url).json()
    subtypes = [page['types'][i]['subTypes'] for i in page['types'].keys()]
    mtgjson_subtypes = sum(subtypes, [])  # concatenate list of lists into singular list
    return mtgjson_subtypes


########################################################################################################################

def likely_combinations(mtcard, subtypes,population_threshold):
    """
    Rather than consider all colour, mana and subtype combinations which are mostly invalid (i.e. white gorgon with cmc
    of 1000), this considers all subtypes, and finds the associated cmc and colour identities for those subtypes. This
    information is then returned so that the benchmark criteria files can be written. The population threshold
    allows for removal of low constituent subtypes to save further time later on.
    :param mtcard: Pandas.DataFrame, the loaded pandas df containing the card information
    :param subtypes: list, a list of all mtgjson subtypes
    :param population_threshold: int, the minimum number of constituents a single subtype can have
    :return dictionary, {subtype:'convertedManaCost':[<float list>], 'colorIdentity:[<str list>]}
    """
    type_info = {a: {'convertedManaCost': [], 'colorIdentity': []} for a in subtypes}  # generate initial dict

    for subtype in type_info:  # for each mtgjson subtype
        subtype_ind = mtcard.index[mtcard['text'].str.contains(subtype, na=False)]  # indices of subtype in passed df
        if len(subtype_ind) >= population_threshold:  # limit number of constituents per benchmark
            for parameter in type_info[subtype]:  # get colour and cmc values for each subtype
                type_info[subtype][parameter] = mtcard.iloc[subtype_ind][parameter].drop_duplicates().tolist()
                # dict values are now a list of the relevant mtcard values

    combinations = {i:type_info[i] for i in type_info if type_info[i] != {'convertedManaCost': [], 'colorIdentity': []}}
    # remove subtypes which have not been modified (i.e. didn't meet threshold level) or are only singular listings

    return combinations

########################################################################################################################

df = mtcard_file('../MTCARDS/')  # most recent MTCARD df
subtypes = mtcard_types('https://mtgjson.com/json/CardTypes.json')
combinations_to_write = likely_combinations(mtcard=df,subtypes=subtypes, population_threshold=5)
