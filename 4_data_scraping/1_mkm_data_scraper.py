import requests
from bs4 import BeautifulSoup
import pandas as pd

########################################################################################################################


def mkm_data_scraper(mkm_url):
    '''
    given a link to mkm list of prices (set table not individual cards) will pull the foil and non foil data for them
    and return the data in a dictionary for further writing with pandas
    :param mkm_url:  url link to the mkm page in question
    :return: dictionary of hardcoded key and list value
    '''
    page = requests.get(mkm_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    card_desc = [i.find('a')['href'] for i in soup.find_all('div', class_ = 'col-12 col-md-8 px-2 flex-column')[1:]]

    nf_shinv = [i.get_text() for i in soup.find_all('span', class_ = 'd-none d-md-inline')[4:]]  # non foil availability
    nf_price_tags = [i for i in soup.find_all('div', class_ = 'col-price pr-2')[1:]]  # non price tags
    nf_upeur = [i.get_text().replace(',', '.').split(' ')[0] for i in nf_price_tags]  # non foil prices (euros)

    f_shinv = [i.get_text() for i in soup.find_all('div', class_ = 'col-availability d-none d-md-flex')[1:]]  # foil av
    f_price_tags = [i for i in soup.find_all('div', class_ = 'col-price d-none d-md-flex')[1:]]  # foil price tags
    f_upeur = [i.get_text().replace(',', '.').split(' ')[0] for i in f_price_tags]  # foil prices (euros)

    return {'card_desc': card_desc, 'nf_shinv': nf_shinv, 'nf_upeur': nf_upeur, 'f_shinv': f_shinv, 'f_upeur': f_upeur}


########################################################################################################################

base_url = 'https://www.cardmarket.com/en/Magic/Products/Singles/Guilds-of-Ravnica' \
      '?mode=&searchString=&idRarity=0&sortBy=sellVolume_desc&perSite=50&site='

df = pd.DataFrame()  # initialise empty dataframe
url_index = 1  # used to cycle through the kk URLs
while True:
    print(f'Scraping instance {url_index}')  # GUI
    scraped_info = mkm_data_scraper(f'{base_url}{url_index}')  # extracted results of scraped page
    if len(scraped_info['card_desc']) == 0:  # i.e. if empty dict value returned because no more values to scrape
        break
    else:
        print(f'Writing instance {url_index}')  # GUI
        index_df = pd.DataFrame(scraped_info)
        df = df.append(index_df, sort=True)  # append data frame to main df for later writing
        url_index += 1  # update for further scraping

file_headers = ['card_desc', 'nf_shinv', 'nf_upeur', 'f_shinv', 'f_upeur']
df.to_csv('GRN.csv', index=False, columns=file_headers)  # write to file with given order of columns

# TODO 1) write to parse all mapped sets and save data to singular csv
# TODO 2) update the database writer to use the shortened mkm url as scraped above for easier mapping.
