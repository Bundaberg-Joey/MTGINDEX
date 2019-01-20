import requests
from bs4 import BeautifulSoup

########################################################################################################################


def mkm_value_scraper(mkm_card_url):
    """
    Given a card's url, the function parses the webpage's html & returns financial data of the instrument
    :param mkm_card_url: the link to the card's mkm webpage displaying the required financial info
    :return: a tuple (number of cards available type=int, price in euros type=float)
    """
    page = requests.get(mkm_card_url)  # mkm page for a given card
    soup = BeautifulSoup(page.content, 'html.parser').find_all(class_='col-6 col-xl-7')  # contains financial info
    shinv = int(soup[2].get_text())  # shares investable of the card listed on mkm at time of scraping
    upeur = float(soup[4].get_text().split(' ')[0].replace(',', '.'))  # price trend listed on mkm in euros
    return shinv, upeur


########################################################################################################################
print(mkm_value_scraper('https://www.cardmarket.com/en/Magic/Products/Singles/Aether+Revolt/Restoration-Specialist'))
