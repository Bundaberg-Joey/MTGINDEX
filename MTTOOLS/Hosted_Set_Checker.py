import requests
from bs4 import BeautifulSoup
import json

########################################################################################################################


def mtgjson_set_fetcher():
    """
    Parses the list of set names hosted on mtgjson and returns them as a list
    :return: List; elements are strings where each element corresponds to a MTG set hosted on mtgjson
    """
    page = requests.get('https://mtgjson.com/json/SetList.json')
    content = page.json()
    mtgjson_names = [i['name'] for i in content]
    return mtgjson_names


########################################################################################################################


def mkm_set_fetcher():
    """
    parses mkm online and returns a list of the card sets currently hosted
    :return: List; elements are strings where each element corresponds to a MTG set hosted on mkm
    """
    page = requests.get('https://www.cardmarket.com/en/Magic/Products/Singles')
    soup = BeautifulSoup(page.content, 'html.parser')
    dropdown = soup.find_all(attrs={'name': 'idExpansion'})[0]  # sets that will be stored in the dropdown menu
    option_tags = dropdown.find_all('option')[1:]  # all set option tags stored in the dropdown menu
    mkm_names = [i.get_text() for i in option_tags]  # all mkm set names listed
    return mkm_names


########################################################################################################################


def main():
    """
    checks currently available online mkm and mtgjson sets against a local list to see if new sets have been added
    :param local_mkm_record: file containing a list of previously scraped set names
    :return: True if online and local files match, False if the two do not match and further investigation is required
    """

    local_set_record = '../MTREFS/hosted_set_lists.json'


    with open(local_set_record, 'r') as f:
        stored_sets = json.load(f)  # open file and load set names into list

    scraped_sets = {'mtgjson':mtgjson_set_fetcher(), 'mkm':mkm_set_fetcher()}  # dict of online sets
    if scraped_sets != stored_sets:
        with open(local_set_record, 'w') as f:
            json.dump(scraped_sets, f, indent=4)  # write the updated list to a file
            return False
    return True


########################################################################################################################

if __name__ == '__main__':
    main()
