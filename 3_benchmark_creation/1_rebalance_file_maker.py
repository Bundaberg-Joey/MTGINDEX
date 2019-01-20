# TODO 1) loops through the criteria file directory and for each file in the directory it
# TODO 2) unpacks the criteria txt file into a series of nested lists to be read and manipulated into a pandas db
# TODO 3) the main db and criteria list are initially stripped of non filter columns to save memory in processing
# TODO 4) This smaller file is then recursively filtered according to criteria
# TODO 5) the fully filtered pandas db is then written to a csv file with the same name as criteria file