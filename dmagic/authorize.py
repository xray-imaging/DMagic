import pathlib
from requests.auth import HTTPBasicAuth

from dmagic import log


__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['basic',
          'read_credentials', ]

debug = False


def read_credentials(filename):
    """
    Read username and password from filename.
    """
    credentials = []
    with open(filename, 'r') as file:
        for line in file:
            username, password = line.strip().split('|')  
            credentials.append((username, password))
    return credentials


def basic(filename):
    """
    Get authorization using username and password contained in filename.
    """
    credentials = read_credentials(filename)

    username          = credentials[0][0]
    password          = credentials[0][1]
    auth = HTTPBasicAuth(username, password)

    return auth


