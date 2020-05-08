import os
import sqlite3
import warnings

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


def establish_connection(*args):
    """Allows for establishing connections to sqlite databases.
    If the database does not exist when making the connection then a new database will be created.

    Parameters
    ----------
    args : iterable of strings.
        Paths to the databases.

    Returns
    -------
    connections : tuple[sqlite connection]
        Each entry is the connection to an sqlite database.
    """
    connections = []
    for db_path in args:
        if not os.path.exists(db_path):
            warnings.warn('sqlite database does not exist, creating db to enable connection', UserWarning)
        conn = sqlite3.connect(db_path)
        connections.append(conn)
    return connections
