import os
import sqlite3

import yaml


def load_yaml(path):
    """Returns contents of yaml file to user as dictionary.

    Parameters
    ----------
    path : str
        Path to yaml file.

    Returns
    -------
    content : dict
        Contents of the yaml file as a dictionary.
    """
    with open(path) as f:
        content = yaml.load(f, Loader=yaml.FullLoader)
    return content


def establish_connection(db_paths):
    """Allows for establishing connections to multiple existing, local, sqlite databases.

    Parameters
    ----------
    db_paths : list[str]
        Paths to the databases.

    Returns
    -------
    connections : tuple[sqlite connection]
        Each entry is the connection to an sqlite database.
    """
    connections = (sqlite3.connect(db) for db in db_paths if os.path.exists(db))
    return connections
