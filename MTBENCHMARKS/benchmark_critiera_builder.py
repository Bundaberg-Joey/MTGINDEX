import pandas as pd
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

    Update: To further ensure benchmark population, benchmark colour ids are now only a list of the main colours used

    :param mtcard: Pandas.DataFrame, the loaded pandas df containing the card information
    :param subtypes: list, a list of all mtgjson subtypes
    :param population_threshold: int, the minimum number of constituents a single subtype can have
    :return dictionary, {subtype:'convertedManaCost':[<float list>], 'colorIdentity:[<str list>]}
    """
    mtgjson_colours = ['R', 'W', 'B', 'U', 'G','[]']
    type_info = {a: {'convertedManaCost': [], 'colorIdentity': []} for a in subtypes}  # generate initial dict

    for subtype in type_info:  # for each mtgjson subtype
        subtype_ind = mtcard.index[mtcard['text'].str.contains(subtype, na=False)]  # indices of subtype in passed df
        if len(subtype_ind) >= population_threshold:  # limit number of constituents per benchmark
            for parameter in type_info[subtype]:  # get colour and cmc values for each subtype
                type_info[subtype][parameter] = mtcard.iloc[subtype_ind][parameter].drop_duplicates().tolist()
                # dict values are now a list of the relevant mtcard values

        subtype_colours = ''.join(type_info[subtype]['colorIdentity'])
        updated_colours = ['\[]' if colour == '[]' else colour for colour in mtgjson_colours if colour in subtype_colours]
        type_info[subtype]['colorIdentity'] =updated_colours

    combinations = {i:type_info[i] for i in type_info if type_info[i] != {'convertedManaCost': [], 'colorIdentity': []}}
    # remove subtypes which have not been modified (i.e. didn't meet threshold level) or are only singular listings

    return combinations

########################################################################################################################

def benchmark_writer(cons_master, qualifier_1, field_1, qualifier_2, field_2, benchmark_name):
    """
    Given two benchmark criteria and their respective fields, this function takes the main constituent database and
    writes the benchmark to a csv file based on the passed qualifiers and fields. The qualifier(s) and field(s) are not
    explicitly named here as mtgjson routinely updates their json formatting. Hence this allows for changes at main
    without needing to change within the function.
    :param cons_master: The master constituent database from the most recent mtgjson download. Contains all cons info
    :param qualifier_1: The card type and or ability
    :param field_1: Location of qualifier within mtgjson structure
    :param qualifier_2: The card CMC or colouridentity
    :param field_2: The location of qualifier within mtgjson structure
    :param benchmark_name: Filename of benchmark (including location)
    :return: None
    """
    cons_df = cons_master[cons_master[field_1].str.contains(qualifier_1, na=False)]  # filter text, ignore blanks
    cons_df = cons_df[cons_df[field_2].str.contains(qualifier_2, na=False)]  # filter text, ignore blanks
    cons_count = len(cons_df.index)
    if cons_count > 0:  # prevent this writing empty benchmarks to file
        cons_df.to_csv(benchmark_name)


########################################################################################################################


def main():
    """
    Given the most recent mtgjson constituent file and list of hosted creature types, this function will reproducibly
    create all the MTGINDEX benchmarks that are either a combination of subtype and cmc OR combination of subtype and
    coloridentity
    """
    df = mtcard_file('../MTCARDS/')  # most recent MTCARD df
    subtypes = mtcard_types('https://mtgjson.com/json/CardTypes.json')  # list of mtgjson subtypes from hosted json
    combinations_to_write = likely_combinations(df,subtypes, population_threshold=5)  # dict of subtypes cmc and color

    mtgjson_keys = ['text', 'convertedManaCost', 'colorIdentity']  # fields used by mtgjson, prone to renaming
    benchmark_location = 'benchmark_rebalance_files/'  # location the benchmark files will be written to

    for a in combinations_to_write:
        for b in combinations_to_write[a][mtgjson_keys[1]]:
            print(F'Parsing:  {a} {b}')
            filename = F'{benchmark_location}MTGINDEX_{a}_{b}.csv'.replace('\\', '')
            benchmark_writer(df, a, mtgjson_keys[0], b, mtgjson_keys[1], benchmark_name=filename)

        for c in combinations_to_write[a][mtgjson_keys[2]]:
            print(F'Parsing:  {a} {c}')
            filename = F'{benchmark_location}MTGINDEX_{a}_{c}.csv'.replace('\\','')
            benchmark_writer(df, a, mtgjson_keys[0], c, mtgjson_keys[2], benchmark_name=filename)


########################################################################################################################

if __name__ == '__main__':
    main()
