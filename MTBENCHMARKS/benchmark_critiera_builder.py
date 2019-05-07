import pandas as pd
import json
import os

########################################################################################################################


def mtcard(path_to_mtcards):
    """
    Because new MTCARD files will be created whenever mtgjson updates, providing the location of the mtcard files allows
    for dynamic loading of the most recent mtgjson file, regardless of name.
    :param path_to_mtcards: relative path to the MTCARDS folder
    :return: Pandas.DataFrame of the latest mtcard file
    """
    mtcard_name = os.listdir(path_to_mtcards)[-1]
    mtcard_df = pd.read_csv(path_to_mtcards+mtcard_name)
    return mtcard_df


########################################################################################################################

df = mtcard('../MTCARDS/')
categories = ['colorIdentity', 'convertedManaCost', 'text']  # use text to search for keywords

print(df.columns)

"""
df = pd.read_csv('../2_database_creation/Card_Databases/Card_Database_422_20190201_1434.csv')
artist_list = df['artist'].drop_duplicates().tolist()

os.chdir('../MTBENCHMARKS_wip/benchmark_criteria_files')
for artist in artist_list:
    new_artist = ''.join([i for i in artist if i.isalpha()])
    filename = f'artist_{new_artist}.json'
    criteria = {'attribute': 'artist', 'operation': '=', 'value': artist}
    to_write = [criteria]
    print(f'writing {filename}')
    with open(filename, 'w') as f:
        f.writelines(json.dumps(to_write))

print('all done')
"""

