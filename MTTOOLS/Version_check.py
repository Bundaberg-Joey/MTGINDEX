import requests
import json
########################################################################################################################


def current_mtgjson_version(json_url):
    """
    Fetches current version number from mtgjson online and returns value as a string
    :param json_url: URL to the json page where mtgjson display the current online version number
    :return: the current online mtgjson version as a string
    """
    page = requests.get(json_url)  # online json file containing version number of mtgjson online
    mtgjson_online_version = page.json()['version']  # parse json to retrieve the online version number
    return mtgjson_online_version


########################################################################################################################


def main():
    """Takes version from mtgjson and compares against stored build version. Returns True if the versions match,
    otherwise it returns false
    :return : Boolean, True if build version and mtgjson version match
    """
    with open('../../MTGINDEX/MTREFS/build_version.json', 'r') as f:
        build_version = json.loads(f.read())['Build']  # loads locally stored build number for comparison
    mtgjson_version = current_mtgjson_version('https://mtgjson.com/json/version.json')  # online version
    return True if mtgjson_version == build_version else False


########################################################################################################################

if __name__ == '__main__':
    main()
