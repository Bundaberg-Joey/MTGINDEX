"""
Benchmark class, for interfacing between mtgindex and mtgjson databases.
"""
import warnings


class Benchmark:
    """Interface between mtgjson and mtgindex databases by grouping and evaluation of benchmark constituents.
    Tracks constituent selection criteria along with constituent IDs and evaluations for given day.
    Evaluation type can vary depending if benchmark is Paper or Foil or MTGO etc.

    Attributes
    ----------
    name : str
        Name or other ID of benchmark.

    criteria : str
        SQL query used to select relevant constituents from database.

    evaluation_date : str
        Date to retrieve evaluation information for benchmark constituents

    evaluation_type : str
        Type of evaluation to consider when accessing constituent evaluations (i.e. Paper vs Foil vs MTGO)

    _constituents : list[str], shape(<num_entries>)
            List of benchmark constituent UUIDs from the mtgjson database.
            Initialises as empty list.

    _values : list[str], shape(<num_entries>)
        List of benchmark constituent values from the mtgjson database.
        Initialises as empty list.

    Methods
    -------
    apply_criteria(self, constituent_table_curr) --> Applies benchmark criteria to select valid constituents.
    evaluate_constituents(self, evaluation_table_curr) --> Looks up evaluations of valid constituents.
    report_data(self) --> Returns select benchmark attributes as dictionary.
    """

    def __init__(self, name, criteria, evaluation_type, evaluation_date):
        """
        Parameters
        ----------
        name : str
            Name or other ID of benchmark.
            
        criteria : str
            SQL query used to select relevant constituents from database.

        evaluation_type : str
            Type of evaluation to consider when accessing constituent evaluations (i.e. Paper vs Foil vs MTGO)
            
        evaluation_date : str
            Date to retrieve evaluation information for benchmark constituents
        """
        self.name = name
        self.criteria = criteria
        self.evaluation_date = evaluation_date
        self._constituents = []
        self._evaluation_type = evaluation_type
        self._values = []

    def apply_criteria(self, constituent_table_curr):
        """Apply benchmark criteria to table of constituents.
        Filters constituents based on SQL query passed at initialisation.
        If no constituents found then UserWarning is raised.
        Updates `constituents` attribute.

        Parameters
        ----------
        constituent_table_curr : sqlite3.Cursor
            Cursor object for the database containing constituent meta data for selection criteria.

        Returns
        -------
        None
        """
        results = constituent_table_curr.execute(self.criteria).fetchall()
        if len(results) > 0:
            self._constituents = [entry[0] for entry in results]
        else:
            warnings.warn(F'No constituents satisfying criteria {self.criteria}', UserWarning)

    def _evaluation_query(self):
        """Generates SQL query used to parse prices table for constituent value information.
        Query wil filter constituents based on date, constituents and type of value to retrieve.
        Type is specified as can have Foil / Online / Paper versions of cards with different evaluations.

        Returns
        -------
        query : str
            Autogenerated SQL query to parse specific constituent values.
        """
        placeholder = '?'
        cons_placeholder = ",".join(placeholder * len(self._constituents))
        query = F'SELECT price FROM prices WHERE type="{self._evaluation_type}" AND date="{self.evaluation_date}" ' \
                F'AND uuid IN ({cons_placeholder})'
        return query

    def evaluate_constituents(self, evaluation_table_curr):
        """Retrieve the values of benchmark constituents from evaluation table.
        Constituents evaluated according to date, constituents, and `_evaluation_type`.
        If no values are found then raises UserWarning.

        Parameters
        ----------
        evaluation_table_curr : sqlite3.Cursor
            Cursor object for the database containing constituent evaluation data.
        Returns
        -------
        None
        """
        query = self._evaluation_query()
        evaluation_table_curr.execute(query, (self._constituents))
        results = evaluation_table_curr.fetchall()

        if len(results) > 0:
            self._values = [entry[0] for entry in results]
        else:
            warnings.warn(F'No values found', UserWarning)

    def report_data(self):
        """Exports internal benchmark information as a dictionary.

        Returns
        -------
        data : dict
            'benchmark': `name` (str),
            'date': `evaluation_date` (str),
            '_value_type': `_evaluation_type` (str),
            'constituents': `_constituents` (list[str]),
            'values': `_values` (list[float])
        """
        data = {
            'benchmark': self.name,
            'date': self.evaluation_date,
            'evaluation_type': self._evaluation_type,
            'constituents': self._constituents,
            'values': self._values
        }
        return data

    def get_constituents(self):
        """Getter for `_constituents`.
        No transformations performed.

        Returns
        -------
        `_constituents` : list[str], shape(<num_entries>)
            List of benchmark constituent UUIDs from the mtgjson database.
        """
        return self._constituents

    def get_values(self):
        """Getter for `_values`.
        No transformations performed.

        Returns
        -------
        `_values` : list[str], shape(<num_entries>)
            List of benchmark constituent values from the mtgjson database.
        """
        return self._values
