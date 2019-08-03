import requests
import json
########################################################################################################################


def main():
    """ Loads locally stored build version and online mtgjson versions and compares them.
    :return : Boolean, True if build version and mtgjson version match, False if they do not match
    """
    with open('../../MTGINDEX/MTREFS/price_version.json', 'r') as f:
        build_version = json.loads(f.read())['Price_Build']  # loads locally stored build number for comparison

    page = requests.get('https://mtgjson.com/json/version.json').json()  # file hosted by mtgjson listing version number
    mtgjson_online_version = page['pricesDate']  # parse json to retrieve the online version number
    return True if mtgjson_online_version == build_version else False


########################################################################################################################

if __name__ == '__main__':
    main()
