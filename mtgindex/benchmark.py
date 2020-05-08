"""
Module Leve Information
"""

class _Benchmark:

    def __init__(self, name, criteria, price_date):
        self.name = name
        self.criteria = criteria
        self.price_date = price_date
        self.constituents = None
        self.values = None

    def apply_criteria(self, constituent_table_curr):
        """Apply benchmark criteria to table of constituents.
        Updates `constituents` attribute.

        Parameters
        ----------
        constituent_table_curr : sqlite3 cursor for db containing constituent information.

        Returns
        -------
        None
        """
        results = constituent_table_curr.execute(self.criteria).fetchall()
        if len(results) > 0:
            self.constituents = [entry[0] for entry in results]
        else:
            self.constituents = []

    def _price_query(self):
        """ Create the query used to extract prices from the cons database"""
        converted_cons = str(tuple(self.constituents))
        query = F'SELECT price FROM prices WHERE type="{self.value_type}" AND date="{self.price_date}" ' \
                F'AND {converted_cons}'  # query should work but will need to test to make sure
        return query

    def evaluate_constituents(self, price_table_curr):
        """Determine the value of each constituent in the database on price date.
        Sources values from exterior price table.

        Parameters
        ----------
        price_table_curr : sqlite3 cursor for db containing price information.

        Returns
        -------
        None
        """
        # need to filter price table based on list of uuids, date and price_type
        price_query = self._price_query()
        results = price_table_curr.execute(price_query).fetchall()
        assert len(results) == len(self.constituents), 'Number of constituents and associated prices do not match'
        self.values = results

    def transcribe_evaluations(self, storage_curr):
        """Export benchmark information so can be saved to a database somehow"""
        details = {'date': self.price_date,
                   'constituents': self.constituents,
                   'value_type': self.value_type,
                   'values': self.values}
        return details


class BenchmarkPaper(_Benchmark):
    value_type = 'paper'


class BenchmarkPaperFoil(_Benchmark):
    value_type = 'paperFoil'


class BenchmarkMtgo(_Benchmark):
    value_type = 'mtgo'


class BenchmarkMtgofoil(_Benchmark):
    value_type = 'mtgoFoil'
