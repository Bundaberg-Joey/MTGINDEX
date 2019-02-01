import json
import pandas as pd
import requests
from collections import Counter
import ast
import os

########################################################################################################################


def card_colour_ids(database_file, database_series):
	"""
	given a pandas dataframe and specified series in that dataframe, will a dictionary of unique entries in series
	:param database_file:  mtgjson database file
	:param database_series: specified column (dataframe dict key) in the passed column
	:return: a dictionary of uique values where key is to be suitable for file naming and value for json saving
	"""
	df = pd.read_csv(database_file)
	colour_count = Counter(df[database_series].tolist())  # all entries converted to Counter object to remove non unique
	stored_colours = [i for i in colour_count]  # keys of Counter, strings are str representations of lists used in db

	filename_colours = []  # strings to be used in the benchmark filename (i.e. can't be in list form)
	for i in colour_count:
		name_chunk = ('').join(ast.literal_eval(i))  # converts str to python list then joins on space
		if name_chunk == '':  # i.e. if there is no associated colour for filename to use
			filename_colours.append('blank')  # use 'blank' as default value
		else:
			filename_colours.append(name_chunk)  # just use this value

	card_colour_ids = {filename_colours[i]:stored_colours[i] for i in range(0, len(filename_colours))}
	return card_colour_ids  # returns dict, keys == used in filenames, values == used in pandas filtering


########################################################################################################################

def card_abilities(json_url):
	"""
	takes url to json page and returns list of keywords len(132) for further utilisaion later
	:param json_url: link to the mtgjson page
	:return: dictionary where keys are to be used in filenames and values are to be used in pandas filtering
	"""
	page = requests.get(json_url)
	data = json.loads(page.content)['KeywordAbilities']
	card_abilities = {i.replace(' ', ''):i for i in data}
	card_abilities['anyabilities'] = ''  # used when wanting to include all cards regardless of ability
	return card_abilities

########################################################################################################################
colour_ids = card_colour_ids('../2_database_creation/Card_Databases/Card_Database_421_20190121_2205.csv', 'colorIdentity')  # Dict as per above function, no issue with pd filtering
abilities = card_abilities('https://mtgjson.com/json/Keywords.json') # This can be filtered for in benchmark creation
cmc = [i for i in range(1,17)] + [1000000] # max of 16 in mtg. Filter works for pd filtering. max due to one UNH card

# 67584 combinations although I reckon a load of them aren't going to be filled


# Need to rewrite because of dictionaries being used
os.chdir('../3_benchmark_creation/benchmark_criteria_files')
for mana in cmc:
    for colour in colour_ids:
        for ability in abilities:
            file_name = f'{mana}_{colour}_{ability}.json'  # issue is being able to properly contain the criteria in the filename
            print(file_name)
            cm = {'attribute': 'convertedManaCost', 'operation': '=', 'value': mana}
            col = {'attribute': 'colorIdentity', 'operation': '=', 'value': colour_ids[colour]}
            crp = {'attribute': 'text', 'operation': 'contain', 'value': abilities[ability]}
            to_write = [cm, col, crp]
            with open(file_name, 'w') as f:
                f.writelines(json.dumps(to_write))



