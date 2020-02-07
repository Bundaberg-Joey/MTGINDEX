import yaml

from mtgindex.Build import MtCard

if __name__ == '__main__':

    with open('MTREF/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    mtcard = MtCard(config['local_version_path'], config['remote_version_url'])

    if mtcard.rebuild_required:
        mtcard.set_db_location(config['local_database_location'])
        mtcard.build_local_database(config['database_url'])
