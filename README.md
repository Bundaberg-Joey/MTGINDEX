# MTGINDEX
## About:
MTGINDEX seeks to take the underlying methodology used in financial benchmarking (i.e. the [MSCI](https://www.msci.com/eqb/methodology/meth_docs/MSCI_IndexCalcMethodology_Jan2019.pdf) ,SP500 and NASDAQ benchmarks) and apply it to the sales from Magic The Gathering (**MTG**).
MTG was chosen as the instrument being traded as currently a great deal of [speculation is conducted on individual card prices](https://www.reddit.com/r/mtgfinance/) rather than assessing the price movement of groups of cards as used in financial benchmarking. 
Currently, index levels are conducted on a price weighting basis rather than market weighting due to the lack of aggregated market shares and value data which can be succesfully mapped to constituents.
There have been many changes with this project over the months due to changes in card price vendors and my own knowledge of python so please consider the project history with a pinch of salt.

The constituent card information for creating the MTG benchmarks and the weekly prices are sourced directly from [MTGJSON](https://mtgjson.com/).
While this does not provide the finer detail of daily price changes, MTGJSON provide weekly card values which can allow for a weekly index level to be constructed and assessed.

There is no real intent to try and make money from this project and it is conducted purely for an educational reference point.
Short term future plans include: 
* A more efficient database solution than concatenating csv files
* Alerts for benchmarks which breach certain thresholds
* Autocorrelation of benchmark returns in an attempt to anticipate suitable investments

Longer term plans include:
* Moving the code to a Raspberry Pi through which data can be accessed
* Construction of a website to allow other MTG fans to view benchmark information

## Code Structure:
The python scripts which currently perform all the rebalance work (creating benchmark files and calculating index levels etc) are located in **MTTOOLS**.
These python scripts are imported into the `main.py` file and are then sequentially executed if a *"rebalance"* of the benchmarks is required.

A Rebalance occurs when new pricing data becomes a available and (or) the content of MTGJSON is updated.
A master **MTCARD** file is generated from the json data hosted at [MTGJSON](https://mtgjson.com/downloads/compiled/), converted to a Pandas DataFrame and then saved as a 2D csv file.
From this list of master constituents, numerous benchmark criteria (i.e. card type, cmc cost, colour identity) are iteratively applied to generate multiple benchmarks of a minimum population count.
Once created, these benchmark constituents are saved to a csv file per benchmark and later parsed to create the benchmark levels stored in the MTINDEX files.
Using the benchmark levels calculated in the MTINDEX files, the overall market trends are then assessed.

A brief overview of each script and directory is presented below: 
* `Card_Database_Creator.py` : Using the freely available [MTGJSON](https://mtgjson.com/) website, this script creates a local database file of all mapped MTG cards, listing all available properties
* `Version_check.py` : This script compares the most recent build version against the [currently hosted](https://mtgjson.com/json/version.json) value and advises if a new card database must be created or further benchmark levels be calculated
* `Benchmark_Builder.py` : Based on the hosted types of cards at MTGJSON, this script iteratively filters the main MTCARD database to create constituent lists for the benchmarks
* `Benchmark_Level_Aggregator.py` : Iterates over all benchmark constituent files and calculates the index level based on a price weighted methodology   
* **MTREFS** Stores all locally referred to files (i.e. local build number for `Version_check.py`)
* **MTCARDS** Stores card databases, each database file is stamped with the MTGJSON version number, Date and time created at
* **MTBENCHMARKS** Stores all constituent csv files, including their weekly prices as provided by MTGJSON
* **MTINDEX** Stores the weekly index levels for each three month period that MTGJSON releases per week
  
  
 ## TODOs:
 1. Create master database to store / append weekly benchmark levels to (must also update index of file to ensure new / old benchmarks are also present)
 2. Design an efficient triage analysis of benchmarks which have recently undergone large changes and advise on purchases
 
  