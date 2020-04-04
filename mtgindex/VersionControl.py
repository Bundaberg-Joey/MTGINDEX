from datetime import datetime

import requests

class VersionController(object):
    """Used for comparing host and local versions of mtgindex database.
    Class contains functionality to fetch versions, compare them, and update reference values.

    Attributes
    ----------
    current : str
        Date / version id of current database build store locally.

    queried : str
        Date / version id of current mtgjson database hosted remotely.

    query_key : str
        Key value used to access hosted json file containing remote version.

    match : boolean
        Initialises as None, converted to True if current and queried match, otherwise False.

    Methods
    -------
    fetch_current(self, location) --> Fetches current version.
    fetch_queried(self, location) --> Fetches remote version.
    compare_versions(self) --> Compares versions.
    format_pricedate(self, current='%Y-%m-%d', out='%Y-%m-%d') --> Allows for date conversion.
    update_current_record(self, location) --> Writes version to file.
    """

    def __init__(self, current=None, queried=None):
        self.current = current
        self.queried = queried
        self.query_key = 'pricesDate'
        self.match = None

    def fetch_current(self, location):
        """Returns the version information of the most recent current database.

        Parameters
        ----------
        location : str
             path to file containing current version information.

        Returns
        -------
        None :
            Updates `self.current`.
        """
        with open(location, 'r') as f:
            current = f.read()
        assert isinstance(current, str) and len(current) > 0, 'Local version file potentially empty, halting'
        self.current = current

    def fetch_queried(self, location):
        """Retrieves the current version of the hosted database.
        Requests the json page hosted by mtgjson containing the remote mtgjson dates.
        JSON Response is indexed with the passed key to retrieve the relevant date as multiple are listed.

        Parameters
        ----------
        location : str
             path to file containing queried version information.

        Returns
        -------
        None :
            Updates `self.queried`.
        """
        page = requests.get(location).json()
        queried = page[self.query_key]
        assert len(queried) > 0, 'Remote version potentially empty, halting'
        self.queried =  queried

    def compare_versions(self):
        """Compares the current and queried versions, updating state as appropriate.

        Returns
        -------
        `self.match`: boolean
            Equivalence of current and queried version.
        """
        self.match = True if self.current == self.queried else False
        return self.match

    def format_pricedate(self, current='%Y-%m-%d', out='%Y-%m-%d'):
        """Converts between the mtgjson date and user specified date format.
        Allows local database to be consistent if the supplier ever changes their date format.

        Parameters
        ----------
        current : str (default = '%Y-%m-%d')
            Date format of the mtgjson date hosted.

        out : str (default = '%Y-%m-%d')
            Date format used for storing price data locally.

        Returns
        -------
        converted : str
            Date in the format specified by `out`
        """
        try:
            converted = datetime.strptime(self.queried, current).strftime(out)
        except ValueError:
            raise ValueError(F'Unable to convert {self.queried} from {current} to {out}')

        return converted

    def update_current_record(self, location):
        """Updates record of current version with that of queried version.
        'self.current' is updated to `self.queried` to reflect update.
        Returns the version information of the most recent current database mtgjson.

        Parameters
        ----------
        location : str
             path to file containing current version information.

        Returns
        -------
        None
        """
        with open(location, 'w') as f:
            f.write(self.queried)
        self.current = self.queried
