import pandas as pd
import json
import os

df = pd.read_csv('../2_database_creation/Card_Databases/Card_Database_422_20190201_1434.csv')
artist_list = df['artist'].drop_duplicates().tolist()

os.chdir('../MTBENCHMARKS_wip/benchmark_criteria_files')
for artist in artist_list:
    new_artist = ''.join([i for i in artist if i.isalpha()])
    filename = f'artist_{new_artist}.json'
    criteria = {'attribute': 'artist', 'operation': '=', 'value': artist}
    to_write = [criteria]
    print(f'writing {filename}')
    with open(filename, 'w') as f:
        f.writelines(json.dumps(to_write))

print('all done')


