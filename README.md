# MTGINDEX

## About:
MTGINDEX seeks to take the underlying methodology used in financial benchmarking (i.e. the [MSCI](https://www.msci.com/eqb/methodology/meth_docs/MSCI_IndexCalcMethodology_Jan2019.pdf),SP500 and NASDAQ benchmarks) and apply it to the sales from the Magic the Gathering game.
Magic the Gathering (MTG) was chosen as the instrument being traded as currently a great deal of [speculation is conducted on individual card prices](https://www.reddit.com/r/mtgfinance/) rather assessing the movement of classess of cards (overall a more efficient analysis). 

The current focus of the project is shifting to developing a dataset that would allow me to start working with ML algorithms for personal developement with the wider scientific python library (i.e. Numpy, SckitLearn and TensorFlow) as the project was intitially created to allow me to gain experience working with python. The prior knowledge required for constructing the benchmarks themselves is taken from my prior experience
working within the financial services sector. (As this was the first acual python project I started working on, please forgive my earlier attempts, they were all part of the learning process).

## Structure:

**MTTOOLS** contains the python scripts that are imported into the main MTRUNNER.py script:
  
  ```Card_Database_Creator.py``` : Using the freely available [MTGJSON](https://mtgjson.com/) website, this script creates a local database file of all mapped MTG cards, listing all available properties
  
  ```Version_check.py``` : Rather than manually check to see if MTGJSON has updated, this script compares the most recent build version against the [currently hosted](https://mtgjson.com/json/version.json) value and advises if a new card database must be created
  
  ```Mkm_Data_Scraper.py``` : Based on mapping conducted between MTGJSON and [Magic Card Market (MKKM)](https://www.cardmarket.com/en/Magic), the mkm website is scraped to retrieve the daily price trends and numbers of cards available (UPEUR and SHINV respectively)
  
  
  **MTREFS** is used to store all locally referred to files (i.e. local build number for ```Version_check.py```)
  
  **MTCARDS** is used to store card databases, each database file is stamped with the MTGJSON version number, Date and time created at
  
  **MTDATA** is used to store the daily scraped instrument data, each file is stamped with the date it was scraped
  
  > Note : While MKM do provide an API service for accessing instrument data, the instrument SHINV is unable to be retreived by this API and therefore the data is scraped. All scraping conducted as part of MTGINDEX strictly obeys the rules laid out by [MKM's robots.txt file](https://www.cardmarket.com/robots.txt)
  
  
