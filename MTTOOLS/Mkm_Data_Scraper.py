import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
from multiprocessing import Pool
########################################################################################################################


def pages_to_scrape():
    """
    scrapes the first page of the mkm singles listing, finds how many pages there are and creates a list of the mkm
    urls needed to scrape. Scraping the first page allows for dynamic generation of the required urls.
    :return: list, urls that need to be scraped
    """
    default_url = 'https://www.cardmarket.com/en/Magic/Products/Singles?perSite=50&site='
    page = requests.get(F'{default_url}{1}')  # first page of mkm singles, 50 cards listed per page
    soup = BeautifulSoup(page.content, 'html.parser')
    pages_tag = soup.find(attrs={'class':'mx-1'}).get_text()  # find string listing "Page 1 of xyz"
    max_pages = int(pages_tag.split(' ')[-1])  # extract string 'xyz' from above and convert to int xyz
    page_list = [F'{default_url}{i}' for i in range(1,max_pages+1)]  # dynamically generate page list
    return page_list


########################################################################################################################


def mkm_data_scraper(mkm_url):
    """
    given a link to mkm list of prices (set table not individual cards) will pull the foil and non foil data for them
    and return the data in a dictionary for further writing with pandas
    :param mkm_url:  string, url link to the mkm page in question
    :return: pd.DataFrame , hardcoded key and list value
                mkm_map =  mkm card url, use to map card info between MTCARD and MTDATA
                nf_shinv = number of non foil cards currently available on mkm
                nf_upeur = price trend of non foil cards currently available on mkm (Euros)
                f_shinv = number of foil cards available on mkm
                f_upeur = price trend of foil cards available on mkm (Euros)
    """
    print(F'  >>> Scraping {mkm_url}')  # GUI
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

    scraped_df = pd.DataFrame({'mkm_map': mkm_card_hrefs,
                                F'nf_shinv_{date_stamp}': nf_shinv,  # date stamp column for time series analysis
                                F'nf_upeur_{date_stamp}': nf_upeur,
                                F'f_shinv_{date_stamp}': f_shinv,
                                F'f_upeur_{date_stamp}': f_upeur})

    return scraped_df


########################################################################################################################


def main():
    """
    Scrapes the mkm singles list and saves information to a pandas dataframe which is later written to a local file
    :return: csv file, The scraped data is organised into a csv file and then written to MTDATA folder
    """
    page_list = pages_to_scrape()  # list of mkm urls to scrape (50 cards per page)
    with Pool(10) as p:  # while running 10 processes at once
        scraped_pages_df = p.map(mkm_data_scraper, page_list)  # apply function to list of urls and save to list

    df = pd.DataFrame()  # initialise empty dataframe
    for partial_df in scraped_pages_df:  # for every dataframe created from scraping mkm
        df = df.append(partial_df, ignore_index=True)  # append to the main df
    df = df.drop_duplicates(keep='first')  # remove potential duplicates

    os.chdir('../../MTGINDEX/MTDATA')  # change directory to where mtgjson card databases are stored
    date_stamp = datetime.now().strftime("%Y%m%d")  # date for filename
    df.to_csv(F'MTDATA_{date_stamp}.csv', index=False)  # write to filename


########################################################################################################################

if __name__ == '__main__':
    main()
