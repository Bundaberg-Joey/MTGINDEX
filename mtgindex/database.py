"""
Interface for mtgindex database.
"""

import sqlite3


class MtgIndex:
    """Class used to interact with the `mtgindex.sqlite` database.
    Allows users to create new benchmarks, add constituent and index values for a certain date and access tables.

    Class is built on the database design as below, where each benchmark has its own table:

            CREATE TABLE table_name (
                evaluationdate DATE,
                constituents TEXT,
                evaluations TEXT,
                indexvalue REAL,
                PRIMARY KEY (evaluationdate));

    Attributes
    ----------
    location : str
        Path to mtgindex database.

    conn : sqlite3.Connection
        Connection to mtgindex database.

    curr : sqlite3.Cursor
        Cursor for mtgindex database connection.

    benchmarks : list[str], shape(num_entries)
        List of table names in mtgindex database (equivalent to names of benchmarks)

    Methods
    -------
    table_exist(self, name) --> Checks if table name already exists in database.
    add_benchmark(self, benchmark_obj) --> Creates new benchmark table.
    update_benchmark_table(self, benchmark_obj) --> Add dated row to benchmark table.
    return_table(self, name) --> Returns the contents of a table as a list of tuples.
    """

    def __init__(self, location):
        """
        Parameters
        ----------
        location : str
            Path to mtgindex database.
        """
        self.location = location
        self.conn = sqlite3.connect(self.location)
        self.curr = self.conn.cursor()
        self.benchmarks = self._update_benchmark_listing()

    def _update_benchmark_listing(self):
        """List the names of tables / benchmarks present within the database.

        Returns
        -------
        cleaned : list[str], shape(<num_tables>)
            List of table names / benchmark names present in the database.
        """
        command = 'SELECT name FROM sqlite_master WHERE type="table"'
        results = self.curr.execute(command).fetchall()
        cleaned = [entry[0] for entry in results]  # otherwise returns as tuples
        return cleaned

    def table_exist(self, name):
        """Allows user to check if table exists wtithin the database or not.
        Refreshes the listing of existing benchmarks before performing comparison.

        Parameters
        ----------
        name : str
            Name of benchmark table in the database.

        Returns
        -------
        exist : bool
            True if the benchmark does exist currently, False otherwise.
        """
        self.benchmarks = self._update_benchmark_listing()
        exist = True if name in self.benchmarks else False
        return exist

    def add_benchmark(self, benchmark_obj):
        """Creates new table in database for passed benchmark object, will raise error if already exists.
        `benchmarks` attribute is updated following the addition of the new table.

        Parameters
        ----------
        benchmark_obj : mtgindex.benchmark.Benchmark
            Benchmark object containing relevant constituents and their evaluations for a given date.

        Returns
        -------
        None
        """
        command = F"""
        CREATE TABLE {benchmark_obj.name} (
            evaluationdate DATE,
            constituents TEXT,
            evaluations TEXT,
            indexvalue REAL,
            PRIMARY KEY (evaluationdate));
        """

        self.curr.execute(command)
        self.benchmarks = self._update_benchmark_listing()  # added new table so need to update

    def update_benchmark_table(self, benchmark_obj):
        """Updates columns {date, constituents, values, index} for the passed benchmark object.
        If benchmark does not already have a table within the database then a new table will be created.

        Parameters
        ----------
        benchmark_obj : mtgindex.benchmark.Benchmark
            Benchmark object containing relevant constituents and their evaluations for a given date.

        Returns
        -------
        None
        """
        name = benchmark_obj.name
        date = benchmark_obj.evaluation_date
        constituents = benchmark_obj.get_constituents_str()
        values = benchmark_obj.get_values_str()
        index_value = benchmark_obj.index_value

        try:
            assert name in self.benchmarks
        except AssertionError:
            self.add_benchmark(benchmark_obj)

        command = F'INSERT INTO {name} (evaluationdate, constituents, evaluations, indexvalue) values (?, ?, ?, ?)'
        self.curr.execute(command, (date, constituents, values, index_value))

    def return_table(self, name):
        """Returns the contents of the specified table frmo the database.
        If table does not exist then will raise ValueError.

        Parameters
        ----------
        name : str
            Name of benchmark table to retrieve.

        Returns
        -------
        table : list[tuple[str]], shape(num_rows, 4)
            Returns the contents of requested table.
        """
        command = F'SELECT * from {name}'
        try:
            assert name in self.benchmarks
            table = self.curr.execute(command).fetchall()
            return table
        except AssertionError:
            raise ValueError(F'Table {name} does not exist within the database')
