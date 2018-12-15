import requests
from bs4 import BeautifulSoup

########################################################################################################################
# Function : given mkm card web link, function will scrape the web page and return SHINV and UPEUR for the card


def mkm_value_scraper(mkm_card_link):
    page = requests.get(mkm_card_link)  # download page
    soup = BeautifulSoup(page.content, 'html.parser')  # create beautiful soup object
    dd_soup = soup.find_all(class_='col-6 col-xl-7')  # filter as required
    card_shinv = int(dd_soup[3].get_text())  # fetched from Available items field, whole number of cards available
    card_up = float(dd_soup[5].get_text().split(' ')[0].replace(',', '.')) * 100  # from price trend field, euro cents

    return card_shinv, card_up


########################################################################################################################
print(mkm_value_scraper('https://www.cardmarket.com/en/Magic/Products/Singles/Tenth+Edition/True-Believer'))

# TODO : have this run through all cards in a given file and append results as a column + calcd caps then sort 