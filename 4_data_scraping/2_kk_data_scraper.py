import requests
from bs4 import BeautifulSoup
import pandas as pd

########################################################################################################################


def value_scraper(kingdom_url):
    """
    Given a URL to magickingdoms search page, will scrape the name, set, price and availability (4 condition types) of
    each card listed (typically 60) or return an empty list if nothing to parse.

    :param kingdom_url: the kingdom URL that needs to be scraped to provide the card data
    :return: Three lists (card href (includes set and card name), prices (4 per card) and availability (4 per card)
            the prices are returned with CCY = USD. 4 values for each card as 4 possible card condition types
    """
    page = requests.get(kingdom_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    price_divs = [i.get_text() for i in soup.find_all(class_='stylePrice')]  # get text from div (all 4 values per card)
    scraped_prices = [price.rstrip().replace(' ', '').replace('$', '') for price in price_divs]  # parse div for value
    scraped_qty = [i.get_text() for i in soup.find_all(class_='styleQty')]  # get availabilities for each card
    scraped_card_info = [i.find('a')['href'] for i in soup.find_all(class_='productDetailTitle')]  # list of card hrefs
    return scraped_card_info, scraped_prices, scraped_qty


########################################################################################################################


def value_writer(scraped_kingdom_data):
    """
    Given a series of scraped data, will split card names into sub lists and the write to a pandas df:

    link --> [ [set_name, card_name], [set_name, card_name], ... ]
    prices -->  [ [NM, VG, G, Other],  [NM, VG, G, Other], ... ]
    conditions -->  [ [NM, VG, G, Other],  [NM, VG, G, Other], ... ]

    This looks complicated but is near instant speeds

    :param scraped_kingdom_data: data that has been passed from scraping the magic card kingdom website
    :return: a pandas dataframe with headers :
    ['set', 'card', 'NM_price', 'NM_qty', 'EX_price', 'EX_qty', 'VG_price', 'VG_qty', 'G_price', 'G_qty']
    """
    card_link, card_prices, card_qty = scraped_kingdom_data  # unpack tuple to variables
    card_facts = [[href.split('/')[-2], href.split('/')[-1]] for href in card_link]  # splits link to list of set & name
    card_cond_prices = [card_prices[i:i + 4] for i in range(0, len(card_prices), 4)]  # turns prices to sublists of 4
    card_cond_qty = [card_qty[i:i + 4] for i in range(0, len(card_qty), 4)]  # turns quantity to sublists of 4

    card_list = []  # will end up containing 60 of the below dictionarys (1 per card)
    for i in range(0,len(card_facts)):
        card_info = {
            'set': card_facts[i][-2],  # set name as per kk
            'card':card_facts[i][-1],  # card name as per kk
            'NM_price':card_cond_prices[i][0], 'NM_qty':card_cond_qty[i][0],  # NM condition information
            'EX_price': card_cond_prices[i][1], 'EX_qty': card_cond_qty[i][1],  # EX condition information
            'VG_price': card_cond_prices[i][2], 'VG_qty': card_cond_qty[i][2],  # VG condition information
            'G_price': card_cond_prices[i][3], 'G_qty': card_cond_qty[i][3]}  # G condition information

        card_list.append(card_info)

    return pd.DataFrame(card_list)


########################################################################################################################

base_url = 'https://www.cardkingdom.com/mtg/guilds-of-ravnica/singles?filter%5Bipp%5D=60&filter%5Bsort%5D=name&page='

df = pd.DataFrame()  # initialise empty dataframe
url_index = 1  # used to cycle through the kk URLs
while True:
    print(f'Scraping instance {url_index}')  # GUI
    scraped_info = value_scraper(f'{base_url}{url_index}')  # extracted results of scraped page
    if len(scraped_info[0]) == 0:  # i.e. if empty list returned because no more values to scrape
        break
    else:
        print(f'Writing instance {url_index}')  # GUI
        df = df.append(value_writer(scraped_info), sort=True)  # append data frame to main df for later writing
        url_index += 1  # update for further scrapring

file_headers = ['set', 'card', 'NM_price', 'NM_qty', 'EX_price', 'EX_qty', 'VG_price', 'VG_qty', 'G_price', 'G_qty']
df.to_csv('GRN.csv', index=False, columns=file_headers)  # write to file with given order of columns
