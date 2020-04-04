import os
import sqlite3

import pandas as pd
from pandas.io import sql


class ConstituentHandler(object):
    """Handles the allocation of constituents to benchmarks using SQL queries of the main database.

    Attributes
    ----------
    conn_origin : sqlite3.Connection
        Connection to the main database containing all constituent information.

    conn_dest : sqlite3.Connection
        Connection to the database containing constituent allocation.

    Methods
    -------
    select_cons(self, benchmark_query) --> fetches matching information from SQL query.

    save_cons(self, name, constituents) --> save constituents to destination database.

    drop_cons_table(self, name) --> drop benchmark from destination database.
    """

    def __init__(self, cons_origin, cons_dest):
        """To prevent loading / writing to erroneous file, existence is checked at initialisation.

        Parameters
        ----------
        cons_origin : str
            Path to database containing constituent information.

        cons_dest : str
            Path to database containing constituent allocations.
        """
        assert os.path.isfile(cons_origin), 'Origin database does not exist'
        assert os.path.isfile(cons_dest), 'Destination database does not exist'
        self.conn_origin = sqlite3.connect(cons_origin)
        self.conn_dest = sqlite3.connect(cons_dest)

    def select_cons(self, benchmark_query):
        """Use passed sql query to load constituent information from the main database.

        Parameters
        ----------
        benchmark_query : str
            An SQL query used to retrieve constituent information.

        Returns
        -------
        valid_cons : DataFrame, shape(number of matches, 1)
            Column dataframe containing unique identifiers of retrieved constituents.
        """
        valid_cons = pd.read_sql(benchmark_query, self.conn_origin)
        return valid_cons

    def save_cons(self, table, constituents):
        """Save passed dataframe to a table in the destination SQL database.

        Parameters
        ----------
        table : str
            Name of the table to save the dataframe to.

        constituents : DataFrame, shape(number of matches, 1)
            Column dataframe containing unique identifiers of retrieved constituents.

        Returns
        -------
        None
        """
        constituents.to_sql(table, self.conn_dest, if_exists='replace', index=False)

    def drop_cons_table(self, table):
        """Removes specified table from the destination database.

        Parameters
        ----------
        table : str
            Name of the table to drop from the database.

        Returns
        -------
        None
        """
        sql.execute(F'DROP TABLE IF EXISTS {table}', self.conn_dest)
