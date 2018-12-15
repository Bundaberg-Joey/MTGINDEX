import pandas as pd  # need module for easy manipulation of the array
import os
########################################################################################################################


def daisy_cutter(card_database, criteria_list):

    """Takes main card database and criteria list, removes all columns except those required for criteria + others
    hence only need to handle a much smaller file for further manipulation / writing"""

    mandatory_headers = ['id', 'mkm_web_link']  # non criteria headers wanted in the rebalance file
    for crit_i in range(0, len(criteria_list)):
        mandatory_headers.append(criteria_list[crit_i][0])  # append benchmark criteria headers
    card_database = card_database[mandatory_headers]  # filter db to only have columns in mandatory headers
    return card_database  # returns significantly smaller db for further iterations than prior versions


########################################################################################################################


def criteria_enforcer(criteria_list, card_db):

    """Takes a list of benchmark criteria and recursively loops through the fed card database to remove invalid cards
    Criteria can either =, >, <, >=, <="""

    if len(criteria_list) > 0:  # checks if there is criteria left to assess
        if criteria_list[0][2] == "=":
            card_db = card_db.loc[card_db[criteria_list[0][0]] == criteria_list[0][1]]  # filter list by criteria ==
            criteria_list.pop(0)  # remove criteria from list so it isn't assessed again
            return criteria_enforcer(criteria_list, card_db)  # run the function again with the assessed criteria removed
        elif criteria_list[0][2] == ">":
            card_db = card_db.loc[card_db[criteria_list[0][0]] > criteria_list[0][1]]  # filter list by criteria >
            criteria_list.pop(0)
            return criteria_enforcer(criteria_list, card_db)
        elif criteria_list[0][2] == "<":
            card_db = card_db.loc[card_db[criteria_list[0][0]] < criteria_list[0][1]]  # filter list by criteria <
            criteria_list.pop(0)
            return criteria_enforcer(criteria_list, card_db)
        elif criteria_list[0][2] == ">=":
            card_db = card_db.loc[card_db[criteria_list[0][0]] >= criteria_list[0][1]]  # filter list by criteria >
            criteria_list.pop(0)
            return criteria_enforcer(criteria_list, card_db)
        elif criteria_list[0][2] == "<=":
            card_db = card_db.loc[card_db[criteria_list[0][0]] <= criteria_list[0][1]]  # filter list by criteria >
            criteria_list.pop(0)
            return criteria_enforcer(criteria_list, card_db)
        elif criteria_list[0][2] == "in":  # used if criteria is a value inside of a stored list / string etc
            card_db = card_db[card_db.filter(like=criteria_list[0][0]).applymap(lambda x: criteria_list[0][1] in x).any(axis=1)]  # magic from online https://stackoverflow.com/questions/39348317/filtering-dataframes-in-pandas-for-multiple-columns-where-a-column-name-contains
            criteria_list.pop(0)
            return criteria_enforcer(criteria_list, card_db)
    else:
        return card_db  # now that he card list is less than 0 (because all criteria have been assessed) return the list


########################################################################################################################


def criteria_unpacker(criteria_file_path):

    """Takes the stored benchmark criteria txt and turns that into a format which allows production of cons arrays"""

    with open(criteria_file_path, 'r') as criteria_file:
        criteria_list = []  # list of lists to be returned
        for criteria in criteria_file.readlines():  # read each line as list
            criteria = criteria.rstrip()  # removes any new line characters that crop up from text file
            criteria = criteria.split('|')  # as reading text file need to split strings via the pipe delimiter
            if criteria[1] in str(range(0, 10)):  # checks if criteria is a number or not
                criteria[1] = int(criteria[1])  # allows numeric strings to be converted to integers, needed for pandas
                criteria_list.append(criteria)
            else:
                criteria_list.append(criteria)  # add to list to be returned
    return criteria_list  # return list of lists to be passed to next function


########################################################################################################################


def main():

    """Purpose : This file creates the rebalance files for all benchmarks stored (rebalance file = all possible constituents)
            1) loops through the criteria file directory and for each file in the directory it
            2) unpacks the criteria txt file into a series of nested lists to be read and manipulated into a pandas db
            3) the main db and criteria list are initially stripped of non filter columns to save memory in processing
            4) This smaller file is then recursively filtered according to criteria
            5) the fully filtered pandas db is then written to a csv file with the same name as criteria file"""

    print(' >> Starting')  # GUI
    card_db_path = os.path.realpath('mtgjson_test.csv')  # db of all cards to carve constituents from
    criteria_folder = os.path.realpath('benchmark_criteria_files')  # folder containing all benchmark criteria files
    rebalance_folder = os.path.realpath('benchmark_rebalance_files')  # folder to write constituent files to

    loaded_card_db = pd.read_csv(card_db_path)  # create pandas DataFrame from card database
    print(' >> Loaded main card database into memory')  # GUI

    for criteria_file in os.listdir(criteria_folder):  # for every criteria file
        os.chdir(criteria_folder)  # need to change directory in order to read the criteria file
        save_name = criteria_file[:-4] + '.csv'  # name the rebalance file will be written with, same as criteria
        print(' >> Creating rebalance file : ' + save_name) # GUI
        (criteria_enforcer(criteria_unpacker(criteria_file), daisy_cutter(loaded_card_db, criteria_unpacker(criteria_file))))\
            .to_csv(rebalance_folder + '\\' + save_name, index=False)  # take criteria file, create a rebalance file from it and save to a csv

    print(' >> All rebalance files now created')  # GUI


########################################################################################################################


if __name__ == '__main__':  # Runs the damn script
    main()
