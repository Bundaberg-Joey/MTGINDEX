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
    mtgjson_online_version = json.loads(page.content)['version']  # parse json to retrieve the online version number
    return mtgjson_online_version


########################################################################################################################


def main():
    """Takes version from mtgjson and compares against stored build version. if difference then prompts user"""
    with open('build_version.json', 'r') as f:
        build_version = json.loads(f.read())['Build']  # loads locally stored build number for comparison

    mtgjson_version = current_mtgjson_version('https://mtgjson.com/json/version.json')
    print(f'MTGJSON_version = {mtgjson_version}')  # GUI
    print(f'Build_version = {build_version}')  # GUI

    if  mtgjson_version == build_version:
        print('Build and Online Versions Match.')  # no need to recreate local database
    else:
        print('Build Version does not equal MTGJSON version')  # should update local db (build version updates during)


########################################################################################################################

if __name__ == '__main__':
    main()  # Checks to see if I need to update the main database or not due to an update of mtgjson data
