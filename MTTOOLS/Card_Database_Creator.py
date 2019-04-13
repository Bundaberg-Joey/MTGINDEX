import requests
import pandas as pd
from pandas.io.json import json_normalize
from datetime import datetime
import json

########################################################################################################################


def build_info():
    """
    Creates a filename for the newly built file and also provides version number used in build
    :return: Dictionary {Filename to be used in MTCARD file,  Full version number for updating the build version file}
    """
    page = requests.get('https://mtgjson.com/json/version.json')
    build_version = page.json()['version']  # takes mtgjson version from their website
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')  # generates time stamp for the database file
    build_name = F'MTCARD_{build_version.replace(".", "")}_{timestamp}.csv'  # filename for new build
    return build_name, build_version


########################################################################################################################


def main():
    """
    Parses all mtg sets hosted by mtgjson. The entire json file is accessed and the database file is built up
    incrementally from the list of sets (json keys). The database is then filtered to remove cards with no mappings
    and it is then written to a csv. The locally stored build version is also updated following this construction.
    """
    page = requests.get('https://mtgjson.com/json/AllSets.json').json()  # extract all information as json
    hosted_sets = page.keys()  # list of sets hosted by mtgjson

    df = pd.DataFrame()
    for mtgjson_set in hosted_sets:
        print(F'Now processing {mtgjson_set}')
        set_df = json_normalize(page[mtgjson_set]['cards'])  # for each set access the card information
        df = df.append(set_df, sort=True)  # append to the main dataframe to be written

    df = df.dropna(subset=['tcgplayerPurchaseUrl'])  # if this is blank then values cannot be mapped so no use

    build_name, build_version = build_info()
    df.to_csv(F'../MTCARDS/{build_name}', index=False)

    with open('../MTREFS/build_version.json', 'w') as f:  # used to update the stored build version
        f.write(json.dumps({"Build": build_version}))  # writes build version to the file


########################################################################################################################

if __name__ == '__main__':
    main()

