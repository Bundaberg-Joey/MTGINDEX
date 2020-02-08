import os
from datetime import datetime
import sqlite3

import requests
import pandas as pd
from  pandas.io import sql

__author__ = 'Calum Hand'
__version__ = '1.0.0'


class MtCard(object):

    def __init__(self, local_path, remote_path, remote_json_key='pricesDate'):
        """
        Creates local versions of the hosted mtgjson data at 'https://mtgjson.com/'.
        On initialisation, both the local and remote mtgjson versions are sourced and compared.
        local is stored in a local file and remote is a hosted json file by mtgjson.
        The user can download the passed sqlite data and save a local version to disk.

        :param local_path:      str, path to the local file containing the recent build version
        :param remote_path:     str, url of the data hosted by mtgjson
        :param remote_json_key: str, json key used to access the relevant date for version comparison

        ::Attributes:
        local_path:         str, path to the local file containing the recent build version
        remote_path:        str, url of the data hosted by mtgjson
        local_version:      str, value of local date version
        remote_version:     str, value of remote version
        rebuild_required:   boolean, evaluates to if the rebuild is needed or not, default False
        date_stamp:         str, date of class initialisation / database creation
        db_location:        str, file name the database is saved to, includes date stamp and extension
        data:               bytes object, retrieved online this database is a non text database file, typically sqlite
        created:            boolean, initially false but sets to True after downloaded database has been written to file

        """
        self.local_path = local_path
        self.remote_path = remote_path
        self.local_version = self._retrieve_local_version()
        self.remote_version = self._retrieve_remote_version(remote_json_key)
        self.rebuild_required = True if self.local_version != self.remote_version else False
        self.date_stamp = datetime.now().strftime('%Y%m%d')
        self.db_location = None
        self.data = None
        self.created = False


    def _retrieve_local_version(self):
        """
        Reads the file containing the date of the most recent local data build

        :return: str, date of most recent local build
        """
        with open(self.local_path, 'r') as f:
            local = f.read()
        return local


    def _retrieve_remote_version(self, json_key):
        """
        Requests the json page hosted by mtgjson containing the remote build dates.
        JSON Response is indexed with the passed key to retrieve the relevant date as multiple are listed.

        :param json_key: str, the json dictionary key that access the date of the specific build type
        :return: str, date of most recent remote build
        """
        page = requests.get(self.remote_path).json()
        assert json_key in page.keys(), 'Passed json key does not exist within mtgjson structure'
        remote = page[json_key]
        return remote


    def set_db_location(self, folder_path, extension='sqlite'):
        """
        Allows user to set the directory which the data will be saved to.
        The data must exist locally and already exist in order to be accepted as valid.

        :param folder_path: str, path the the directory which the user wishes to save to
        """
        assert isinstance(folder_path, str) and isinstance(extension, str), 'Path and extension must be type Strings'
        assert os.path.isdir(folder_path), 'Passed path must already exist'
        file_name = F'MTCARD_{self.date_stamp}.{extension}'
        self.db_location = os.path.join(folder_path, file_name)


    def _retrieve_data(self, data_url):
        """
        Retrieves the hosted data from mtgjson and checks that a successful response has been received.
        The `data` attribute is then updated with the response content.

        :param data_url: str, url of the sqlite database hosted by mtgjson
        """
        response = requests.get(data_url)
        response.raise_for_status()
        self.data = response.content


    def build_local_database(self, data_url, write_mode='wb'):
        """
        Creates a local version of the hosted mtgjson, sqlite database with suitable name and extension.

        :param data_url: str, url of the sqlite database hosted by mtgjson
        :param write_mode: str, allows for switching between binary / non binary formats in the future
        """
        assert isinstance(data_url, str), 'Passed data url must be a string'
        assert write_mode in ['w', 'wb'], 'Write mode must be to only write as text or binary only, '

        self._retrieve_data(data_url)
        with open(self.db_location, write_mode) as f:
            f.write(self.data)
        self.created = True


    def update_local_version(self):
        """
        Updates the locally stored build version with the remote version if the local data has been built.
        The `local_version` attribute is then updated to the `remote_version` value.
        """
        assert self.created is not False, 'Do not update local version until build completed'

        with open(self.local_path, 'w') as f:
            f.write(self.remote_version)

        self.local_version = self.remote_version


########################################################################################################################


class MtBenchmark(object):

    def __init__(self, mtcard_location, mtbenchmark_location):
        """
        Builds the benchmarks which are assessed as part of MTGINDEX.
        Benchmarks constituents are allocated based on saved sql queries (from MTCARD) allowing for easy addition of
        new benchmarks with peculiar criteria in a reproducible manner.

        :param mtcard_location:         str, path to sqlite database downloaded from mtgjson
        :param mtbenchmark_location:    str, path to sqlite database containing benchmark constituent allocations

        ::Attributes:
        self.conn_mtcard:           sqlite3.Connection, connection to mtcard sql database
        self.conn_mtbenchmark:      sqlite3.Connection, connection to mtbenchmark sql database

        """
        self.conn_mtcard = sqlite3.connect(mtcard_location)
        self.conn_mtbenchmark = sqlite3.connect(mtbenchmark_location)


    @staticmethod
    def _load_queries_from_file(path_to_queries):
        """
        Loads the sql queries and benchmark names and returns them as a generator of the form: (index, row)

        :param path_to_queries: str, file containing benchmark names and sql queries to allocate constituents
        :return: loaded_queries: generator,
        """
        df = pd.read_csv(path_to_queries, index=False)
        loaded_queries = df.iterrows()
        return loaded_queries


    def allocate_constituents(self, path_to_queries):
        """
        During a rebalance, the constituents of the MTCARD database will need to be redistributed according to their
        selection criteria for inclusion (i.e. convertedManaCost> 10).
        This is handled buy loading the SQL queries used to generate the benchmarks originally and applying them to
        the passed mtcard database.
        The uuids of the valid constituents are then written to their own table within the mtbenchmark database.
        If a benchmark has no valid constituents then the table is dropped from the mtbenchmark database.

        :param path_to_queries: str, file containing benchmark names and sql queries to allocate constituents
        """
        assert os.path.isfile(path_to_queries), 'Specified path is not valid'

        benchmark_generator = self._load_queries_from_file(path_to_queries)

        for _, row in benchmark_generator:
            name, generation = row
            valid_constituents = pd.read_sql(generation, self.conn_mtcard)

            if valid_constituents.size > 0:
                valid_constituents.to_sql(name, self.conn_mtbenchmark, if_exists='replace', index=False)
            else:
                sql.execute(F'DROP TABLE IF EXISTS {name}', self.conn_mtbenchmark)

