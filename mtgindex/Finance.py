import pandas as pd


class BenchmarkHandler(object):

    def __init__(self, constituent_conn, benchmark_conn):
        self.cons_conn = constituent_conn
        self.bench_conn = benchmark_conn

    def initialise_benchmark_level(self, benchmark, date, value=1000.0):
        """Creates first benchmark level of new benchmark in new sql table.
        New table has the below schema

        Parameters
        ----------
        benchmark : str
            Name of the table to save the benchmark level to.

        date : str
            Date the benchmark is considered to have started on.

        value : float
            Value to use as the first benchmark value

        Returns
        -------
        None
        """
        assert isinstance(value, float), 'New benchmark value must be type float'
        df = pd.DataFrame([{'Date': pd.to_datetime(date), 'Value': value}])
        df = df.set_index('Date')
        df.to_sql(benchmark, self.bench_conn, if_exists='fail')

    def update_benchmark_level(self):
        """ Used if prior benchmark value and cons values for today.
        Insert the new benchmark value into the database.

        Returns
        -------
        None
        """
        # load benchmark as pandas dataframe
        # add new value as row to the dataframe
        # write the update table to sql file
        return NotImplementedError

    def null_benchmark_level(self):
        """ Used if no longer valid constituents so need to propagate a nan value (or equivalent)

        Returns
        -------
        None
        """
        # load benchmark as pandas dataframe
        # add NaN as row to the dataframe
        # write the update table to sql file
        return NotImplementedError


def price_weighted_index(prior_level, constituent_prices, **kwargs):
    """Calculates a price weighted index level based on returns.
    All constituents are assumed to hold an equally weighted contribution to the index (sum of weights is 1).
    level_t = level_{t-1} \times (1 + \sum_{i=0} c_i \cdot w_i)

    Returns
    -------
    None
    """
    # weighting = 1/len(constituent_prices)
    # level = prior_level * (1 + sum(constituent_prices) * weighting)
    # return level
    return NotImplementedError