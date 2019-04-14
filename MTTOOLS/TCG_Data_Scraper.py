import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from multiprocessing import Pool

########################################################################################################################


def pages_to_scrape():
    """
    scrapes the first page of the mkm singles listing, finds how many pages there are and creates a list of the mkm
    urls needed to scrape. Scraping the first page allows for dynamic generation of the required urls.
    :return: list, urls that need to be scraped
    """
    base_url = 'https://shop.tcgplayer.com/price-guide/magic/'
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    all_tags = [i['value'] for i in soup.find_all('option')]  # all tags containing the tcg set names
    start_index = all_tags.index('zombie-world-order-tcg')  # other things in the dropdown tags which need to be removed
    tcg_sets = [base_url + tcg for tcg in all_tags[start_index + 1:]]
    return sorted(tcg_sets)


########################################################################################################################


def tcg_data_scraper(tcg_url):
    """
    given a link to a tcg card set, will extract card href data for mapping and price data which is returned in a pd
    DataFrame. To ensure that as many cards as possible will have a price value for a given date, a MTGINDEX column
    is also returned in the DataFrame which will attempt to populate a price if the main price column is empty.
    All prices are quoted in USD.

    :param tcg_url:  string, url link to the tcg page which is to be scraped

    :return: pd.DataFrame , hardcoded key and list value
                tcg_map =  tcg card url, use to map card info between MTCARD and MTDATA
                MTGINDEXPrice = Combined column from all prices to ensure as many cards are populated
                tcgMarketPrice = compiled from recent, completed sales on tcgplayer.com
                tcgBuyListMarketPrice = based on recently processed and completed purchases of cards through tcg buylist
                tcgMedianPrice = edian from all listed prices for a product based on listed prices only
    """
    print(F'  >>> Scraping {tcg_url}')  # GUI
    page = requests.get(tcg_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    tcg_card_hrefs = [card.find('a')['href'] for card in soup.find_all(attrs={'class': 'productDetail'})]

    price_class_tags = ['marketPrice', 'buylistMarketPrice', 'medianPrice']  # tags containing each of the price types
    card_prices = []
    for class_tag in price_class_tags:
        class_non_formatted = [i.find('div').get_text().strip() for i in soup.find_all(attrs={'class': class_tag})]
        class_formatted = []  # need to remove punctuationto properly populate the pandas df
        for entry in class_non_formatted:
            entry = entry.replace('$', '').replace('—', '').replace(',', '')  # punctuation to be removed
            class_formatted.append(entry)
        card_prices.append(class_formatted)

    full_prices = []
    for position, card in enumerate(card_prices[0]):  # for each card, checks if a price is listed, if not defaults
        if card_prices[0][position] == '':            # to next price type
            if card_prices[2][position] == '':
                if card_prices[1][position] == '':
                    full_prices.append('')  # will return a blank if no pricing data is available at all
                else:
                    full_prices.append(card_prices[1][position])
            else:
                full_prices.append(card_prices[2][position])
        else:
            full_prices.append(card_prices[0][position])

    date_stamp = datetime.now().strftime("%Y%m%d")
    scraped_df = pd.DataFrame({'tcg_map': tcg_card_hrefs,
                               F'MTGINDEXPrice_{date_stamp}': full_prices,
                               F'tcgMarketPrice_{date_stamp}': card_prices[0],
                               F'tcgBuyListMarketPrice_{date_stamp}': card_prices[1],
                               F'tcgMedianPrice_{date_stamp}': card_prices[2]})

    return scraped_df


########################################################################################################################


def main():
    """
    Scrapes the tcg set lists and saves the information to a pandas dataframe which is later written to a local file
    :return: csv file, The scraped data is organised into a csv file and then written to MTDATA folder
    """
    page_list = pages_to_scrape()[:5]  # list of tcg urls to scrape
    with Pool(10) as p:  # while running 10 processes at once
        scraped_pages_df = p.map(tcg_data_scraper, page_list)  # apply function to list of urls and save to list

    df = pd.DataFrame()  # initialise empty dataframe
    for partial_df in scraped_pages_df:  # for every dataframe created from scraping mkm
        df = df.append(partial_df, ignore_index=True)  # append to the main df
    df = df.drop_duplicates(keep='first')  # remove potential duplicates

    build_name = F'MTDATA_{datetime.now().strftime("%Y%m%d")}.csv'  # date for filename
    df.to_csv(F'../MTDATA/{build_name}', index=False)  # write to filename
    print(F'  >>> MTDATA is size {df.shape}')
    print(df.head())
    print(df.tail())


########################################################################################################################

if __name__ == '__main__':
    main()
