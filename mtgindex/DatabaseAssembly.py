import requests

class Assembler(object):
    """Creates local database from hosted data; can be instantiated with data or factory method.

    Attributes
    ----------
    data : None (initially), data structure capable of being written to file
        The hosted data is retrieved and stored.
        So long as the data can easily be written to file, all data formats are valid.

    built : bool
        Boolean value to indicate if the database has been successfully built or not.

    Methods
    -------
    retrieve_data(cls, location) --> Class, factory method for accessing remote data, retrieved by url

    mtcard(self, location) --> Saves `self.data` to specified type
    """

    def __init__(self, data=None):
        """
        Parameters
        ----------
        data : data storage type
            A data format capable of easily being saved to a file.
        """
        self.data = data
        self.built = False

    @classmethod
    def download_data(cls, location):
        """Factory method to retrieve remotely hosted data and return to class.

        Parameters
        ----------
        location : str
            url of hosted database

        Returns
        -------
        Instantiated `Assembler` object.
        """
        response = requests.get(location)
        response.raise_for_status()
        return cls(response.content)

    def get_data(self):
        """Property getter method for accessing data attribute.

        Returns
        -------
        self.data : data structure
        """
        return self.data


class AssembleSQL(Assembler):
    """Child class for saving retrieved data as new SQL database.
    """
    def build(self, destination):
        """ Assemble retrieved database as sqlite file.

        Parameters
        ----------
        destination : str
            filename to save the database to.

        Returns
        -------
        None:
            Sets `self.built` to True.
        """
        assert self.data is not None, 'Data does not exist to mtcard local database'
        with open(destination, 'wb') as f:
            f.write(self.data)
        self.built = True
