import requests
from bs4 import BeautifulSoup

########################################################################################################################


def mkm_sets():
    """
    parses mkm online and returns a list of the card sets currently hosted
    :return: a list of sets currently available on mkm
    """
    page = requests.get('https://www.cardmarket.com/en/Magic/Products/Singles')
    soup = BeautifulSoup(page.content, 'html.parser')
    dropdown = soup.find_all('option')  # sets stored in dropdown functionality
    set_info = {i['value']: i.get_text() for i in dropdown}  # get all options from the drop down menu as dict
    numerical_keys = sorted([int(i) for i in set_info.keys() if i.isdigit()])  # list of integers used as dict keys
    sorted_set = {i: set_info[str(i)] for i in numerical_keys}  # create an "ordered dict, i.e. in order mkm brought out
    return [sorted_set[i] for i in sorted_set]  # return an ordered list


########################################################################################################################


def main():
    """
    checks currently available online mkm sets against a local list to see if there have been any new sets released
    :param local_mkm_record: file containing a list of previously scraped set names
    :return: True if online and file match, False if need to map further
    """

    local_mkm_record = '../MTREFS/mkm_set_list.txt'

    with open(local_mkm_record, 'r') as f:
        stored_names = [i.rstrip() for i in f.readlines()]  # open file and load set names into list

    online_sets = mkm_sets()  # list of online sets
    for mkm_set in online_sets:  # for entry in sets
        if mkm_set not in stored_names:  # if that set is not stored locally then need to update
            with open(local_mkm_record, 'w') as f:
                f.writelines([i + '\n' for i in online_sets])  # write the updated list to a file
            return False
    return True


########################################################################################################################

if __name__ == '__main__':
    main()
