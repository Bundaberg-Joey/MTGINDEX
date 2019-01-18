import requests
import json
########################################################################################################################


def current_mtgjson_version():
    """Fetches current version number from mtgjson online and returns value as a string"""
    page = requests.get('https://mtgjson.com/json/version.json')  # json file containing version number
    mtgjson_online_version = json.loads(page.content)['version']  # parsed json containing
    return mtgjson_online_version


########################################################################################################################


def main():
    """Takes version from mtgjson and compares against stored build version. if difference then prompts user"""
    with open('build_version.json', 'r') as f:
        build_version = json.loads(f.read())['Build']

    mtgjson_version = current_mtgjson_version()
    print(f'MTGJSON_version = {mtgjson_version}')
    print(f'Build_version = {build_version}')

    if  mtgjson_version == build_version:
        print('Build and Online Versions Match.')
    else:
        print('Build Version does not equal MTGJSON version')


########################################################################################################################

if __name__ == '__main__':
    main()  # Checks to see if I need to update the main database or not due to an update of mtgjson data
