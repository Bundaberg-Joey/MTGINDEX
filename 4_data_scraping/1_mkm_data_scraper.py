import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
########################################################################################################################


def mkm_data_scraper(mkm_url):
    """
    given a link to mkm list of prices (set table not individual cards) will pull the foil and non foil data for them
    and return the data in a dictionary for further writing with pandas
    :param mkm_url:  url link to the mkm page in question
    :return: dictionary of hardcoded key and list value
    """
    page = requests.get(mkm_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    card_desc = [i.find('a')['href'] for i in soup.find_all('div', class_='col-12 col-md-8 px-2 flex-column')[1:]]

    nf_shinv = [i.get_text() for i in soup.find_all('span', class_='d-none d-md-inline')[4:]]  # non foil availability
    nf_price_tags = [i for i in soup.find_all('div', class_='col-price pr-2')[1:]]  # non price tags
    nf_upeur = [i.get_text().replace(',', '.').split(' ')[0] for i in nf_price_tags]  # non foil prices (euros)

    f_shinv = [i.get_text() for i in soup.find_all('div', class_='col-availability d-none d-md-flex')[1:]]  # foil av
    f_price_tags = [i for i in soup.find_all('div', class_='col-price d-none d-md-flex')[1:]]  # foil price tags
    f_upeur = [i.get_text().replace(',', '.').split(' ')[0] for i in f_price_tags]  # foil prices (euros)

    return {'card_desc': card_desc, 'nf_shinv': nf_shinv, 'nf_upeur': nf_upeur, 'f_shinv': f_shinv, 'f_upeur': f_upeur}


########################################################################################################################


def price_set_scraper(mkm_set):
    """
	For a given mkm set, will take the parsed webpage data, cycle through urls until a blank list is returned and then
	write the contents of the dataframe to a df and then return it

	:param mkm_set: name of the set in magic card market format (passed as a string)
	:return: a pandas dataframe, containing the scraped data for an entire set
	"""
    set_df = pd.DataFrame()  # initialise an empty dataframe for the card set
    url_index = 1  # set first page to be scraped (number corresponds to the page number)

    mkm_set_url = f'https://www.cardmarket.com/en/Magic/Products/Singles/{mkm_set}' \
                  f'?mode=&searchString=&idRarity=0&sortBy=sellVolume_desc&perSite=50&site='  # link to be scraped

    while True:
        print(f'Scraping {mkm_set} {url_index}')  # GUI
        scraped_data = mkm_data_scraper(f'{mkm_set_url}{url_index}')  # extracted results of scraped page
        key_to_check = list(scraped_data.keys())[0]  # i.e. get first key value in the dict, saves hard coding
        if len(scraped_data[key_to_check]) == 0:  # if empty dict value returned because no more values to scraped
            return set_df  # card data for the initially passed set
        else:
            index_df = pd.DataFrame(scraped_data)  # a dataframe made from a sets specific index
            set_df = set_df.append(index_df, sort=True)  # append data frame to main df for later writing
            url_index += 1  # update for further scraping and repeat while loop with updated index


########################################################################################################################


def main():
    """
    Given a list of mkm sets, will parse the webpages and save the scraped card price / availability data to csv. The
    script will save incremental progress (i.e. for each set will write the entire db to a file, and then write the
    final database to a differently named file (file stamped with date of scraping).
    :return: a database of all scraped card info
    """
    mkm_set_list = pd.read_json('../2_database_creation/v4_mapped_sets.json')['mkm_web_name']  #  mkm sets to parse

    os.chdir('../4_data_scraping/mkm_Databases')  # directory that scraped data files will be written to

    date_stamp = datetime.now().strftime("%Y%m%d")  # date for filename
    file_headers = ['card_desc', 'nf_shinv', 'nf_upeur', 'f_shinv', 'f_upeur']  # order of columns to write file

    df = pd.DataFrame()  # initialise empty dataframe
    partial_count = 1  # keep track of partial files created
    for mkm_set in mkm_set_list:  # for every mkm set in the list of mapped sets
        set_df = price_set_scraper(mkm_set)  # pandas df containing the data for a passed set code
        df = df.append(set_df)  # add to main df to be eventually written
        df = df.drop_duplicates(keep='first')  # strips duplicates from multiple mapped card sets
        df.to_csv(f'Partial_{date_stamp}_{partial_count}.csv', index=False, columns=file_headers)  # write to csv file
        partial_count +=1  # update partial file tracker

    df.to_csv(f'mkm_database_{date_stamp}.csv', index=False, columns=file_headers)  # write to file with given name

    file_list = [i for i in os.listdir(os.getcwd())]  # list of all files stored in the price database folder
    if f'mkm_database_{date_stamp}.csv' in  file_list:  # check to see if today's full file exists
        print('Full database exists deleting partial files')  # GUI
        for written_file in file_list:  # for every file in the file folder
            if 'Partial_' in written_file:  # if this file is a partial file / i.e. not total database
                os.remove(written_file)  # delete the file form the directory
        print('Partial files deleted')  # GUI
    else:
        print('Error full database does not exist for the day, incremental files retained')  # GUI

########################################################################################################################

if __name__ == '__main__':
    main()
