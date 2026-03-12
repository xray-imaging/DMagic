from requests.auth import HTTPBasicAuth

from dmagic import log


__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['basic',
          'read_credentials', ]


def read_credentials(filename):
    """
    Read username and password from filename.

    The file should contain one line in the format: username|password
    """
    try:
        with open(filename, 'r') as file:
            line = file.readline().strip()
    except FileNotFoundError:
        log.error('Credentials file not found: %s' % filename)
        log.error('Create it with: echo "username|password" > %s' % filename)
        return None
    except PermissionError:
        log.error('Permission denied reading credentials file: %s' % filename)
        return None
    except Exception as e:
        log.error('Error reading credentials file %s: %s' % (filename, str(e)))
        return None

    if not line:
        log.error('Credentials file is empty: %s' % filename)
        return None

    parts = line.split('|')
    if len(parts) != 2:
        log.error('Invalid credentials format in %s. Expected: username|password' % filename)
        return None

    username, password = parts[0].strip(), parts[1].strip()
    if not username or not password:
        log.error('Username or password is empty in credentials file: %s' % filename)
        return None

    return username, password


def basic(filename):
    """
    Get HTTP Basic authorization using username and password contained in filename.

    Returns
    -------
    auth : HTTPBasicAuth or None
        Authorization object, or None if credentials could not be read.
    """
    credentials = read_credentials(filename)
    if credentials is None:
        return None

    username, password = credentials
    return HTTPBasicAuth(username, password)


