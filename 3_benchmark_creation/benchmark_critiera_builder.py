import json
import pandas as pd
import requests
from collections import Counter
import ast

########################################################################################################################


def card_colour_ids(database_file):
	df = pd.read_csv(database_file)
	colour_count = Counter(df['colorIdentity'].tolist())  # all entries converted to Counter object to remove non unique
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
colour_ids = card_colour_ids('Card_Database_421_20190123_2133.csv')  # Dict as per above function, no issue with pd filtering
abilities = card_abilities('https://mtgjson.com/json/Keywords.json') # This can be filtered for in benchmark creation
cmc = [i for i in range(1,17)] + [1000000] # max of 16 in mtg. Filter works for pd filtering. max due to one UNH card

# 67584 combinations although I reckon a load of them aren't going to be filled


# Need to rewrite because of dictionarys being used
for mana in cmc:
	for colour in colour_ids:
		for ability in abilities:
			file_name = f'{mana}_{colour}_{ability}.json'  # issue is being able to properly contain the criteria in the filename
			print(file_name)
			#cm = {'attribute': 'cmc', 'operation': '=', 'value': mana}
			#col = {'attribute': 'color', 'operation': '=', 'value': colour_ids[colour]}
			#crp = {'attribute': 'text', 'operation': 'contain', 'value': abilities[ability]}
			#to_write = [cm, col, crp]
			#with open(file_name, 'w') as f:
			#	f.writelines(json.dumps(to_write))



