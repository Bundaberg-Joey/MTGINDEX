import sqlite3

import numpy as np


class MtgIndex:

    def __init__(self, location):
        self.location = location
        self.conn = sqlite3.connect(self.location)
        self.curr = self.conn.cursor()
        self.benchmarks = []  # list of tables in database
        self._new_schema = ''  # sql schema for new database table
        self._new_index_level = 1000.0  # value for new benchmarks to have
        self._propagte_value = np.nan # value to put as index level if no constituents
        self._calculator = '' # function to be passed with getter / setter for calculation of index levels

    def check_benchmark_exists(self):
        pass

    def create_benchmark_table(self):
        pass

    def update_benchmark_table(self):
        pass

    def propagate_null_benchmark(self):
        pass