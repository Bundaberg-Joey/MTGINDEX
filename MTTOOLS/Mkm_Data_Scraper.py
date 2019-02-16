import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
########################################################################################################################


def pages_to_scrape():
    """
    scrapes the first page of the mkm singles listing, finds how many pages there are and creates a list of numbers
    for use in later links
    :return: list of numbers to be used in later scraping
    """
    page = requests.get('https://www.cardmarket.com/en/Magic/Products/Singles?perSite=50&site=1')  # first page of mkm singles, 50 per page
    soup = BeautifulSoup(page.content, 'html.parser')  # bs4 object
    pages_tag = soup.find(attrs={'class':'mx-1'}).get_text()  # find string listing "Page 1 of xyz"
    max_pages = int(pages_tag.split(' ')[-1])  # extract 'xyz' and convert to int
    page_list = list(range(1,max_pages+1))  # create list of integers from 1 to and including above int
    return page_list


########################################################################################################################


def mkm_data_scraper(mkm_url):
    """
    given a link to mkm list of prices (set table not individual cards) will pull the foil and non foil data for them
    and return the data in a dictionary for further writing with pandas
    :param mkm_url:  url link to the mkm page in question
    :return: pd.DaataFrame of hardcoded key and list value
    """
    page = requests.get(mkm_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    mkm_card_hrefs = [i.find('a')['href'] for i in soup.find_all('div', class_='col-12 col-md-8 px-2 flex-column')[1:]]
    # mkm's internal url for the card, can use these to map the cards between dates and mtgjson

    nf_shinv = [i.get_text() for i in soup.find_all('span', class_='d-none d-md-inline')[4:] if i.get_text() != '']
    nf_price_tags = [i for i in soup.find_all('div', class_='col-price pr-sm-2')[1:]]  # non price tags
    nf_upeur = [i.get_text().replace(',', '.').split(' ')[0] for i in nf_price_tags]  # non foil prices (euros)

    f_shinv = [i.get_text() for i in soup.find_all('div', class_='col-availability d-none d-md-flex')[1:]]  # foil av
    f_price_tags = [i for i in soup.find_all('div', class_='col-price d-none d-md-flex')[1:]]  # foil price tags
    f_upeur = [i.get_text().replace(',', '.').split(' ')[0] for i in f_price_tags]  # foil prices (euros)

    date_stamp = datetime.now().strftime("%Y%m%d")  # date for column

    scraped_df = pd.DataFrame({'mkm_map': mkm_card_hrefs,  # mkm card url, use to map between mtgjson and other prices
                                f'nf_shinv_{date_stamp}': nf_shinv,  # date stamp column for time series analysis
                                f'nf_upeur_{date_stamp}': nf_upeur,
                                f'f_shinv_{date_stamp}': f_shinv,
                                f'f_upeur_{date_stamp}': f_upeur})

    return scraped_df


########################################################################################################################


def main():
    """
    Scrapes the mkm singles list and saves information to a pandas dataframe which is later written to a local file
    :return: Written file of the day's prices
    """
    df = pd.DataFrame()  # initialise empty dataframe
    page_list = pages_to_scrape()  # list of integers to be used in scraping url
    for entry in page_list:
        print('Scraping {} of {}'.format(entry, page_list[-1]))
        url_to_scrape = 'https://www.cardmarket.com/en/Magic/Products/Singles?perSite=50&site={}'.format(entry)
        entry_df = mkm_data_scraper(url_to_scrape)  # transient pandas df created for the passed url
        df = df.append(entry_df, ignore_index=True)  # add to main df to be eventually written
    df = df.drop_duplicates(keep='first')  # strips duplicates from multiple mapped card sets

    os.chdir('../../MTGINDEX/MTDATA')  # change directory to where mtgjson card databases are stored
    date_stamp = datetime.now().strftime("%Y%m%d")  # date for filename
    df.to_csv('MTDATA_{}.csv'.format(date_stamp), index=False)  # write to filename


########################################################################################################################

if __name__ == '__main__':
    main()

# TODO : Look into multiprocessing to speed up the scraping of the pages here https://medium.com/python-pandemonium/how-to-speed-up-your-python-web-scraper-by-using-multiprocessing-f2f4ef838686
