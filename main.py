import yaml
import os

from mtgindex.VersionControl import VersionController
from mtgindex.DatabaseAssembly import AssembleSQL

if __name__ == '__main__':
    with open('MTREF/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    vc = VersionController()
    vc.fetch_current(config['local_version_path'])
    vc.fetch_queried(config['remote_version_url'])

    if vc.compare_versions() == False:
        db = AssembleSQL.retrieve_data(config['database_url'])
        save_name = os.path.join(config['local_database_location'], '_safe_to_delete.sqlite')
        db.build(save_name)
