"""
Read the tomolog history file (.tomolog) to retrieve the Google Slides
presentation URL for a given GUP proposal number.

The .tomolog file is a YAML list of dicts written by the tomolog package.
Each entry has at minimum: gup, date, presentation_url.
"""

import os
import yaml

from dmagic import log

TOMOLOG_FILE = '.tomolog'


def get_presentation_url(gup, tomolog_home):
    """Return the most recent Google Slides presentation URL for *gup*.

    Reads ``{tomolog_home}/.tomolog``, filters entries matching the given
    GUP number, sorts by the ``date`` field, and returns the
    ``presentation_url`` of the most recent entry.

    Parameters
    ----------
    gup : str or int
        GUP proposal number to search for.
    tomolog_home : str
        Directory containing the ``.tomolog`` file.

    Returns
    -------
    str or None
        Presentation URL, or None if not found or file cannot be read.
    """
    tomolog_path = os.path.join(tomolog_home, TOMOLOG_FILE)

    if not os.path.isfile(tomolog_path):
        log.warning('tomolog history file not found: %s' % tomolog_path)
        return None

    try:
        with open(tomolog_path, 'r') as f:
            history = yaml.safe_load(f)
    except Exception as e:
        log.warning('Could not read tomolog history file %s: %s' % (tomolog_path, str(e)))
        return None

    if not isinstance(history, list):
        log.warning('Unexpected format in tomolog history file: %s' % tomolog_path)
        return None

    gup_str = str(gup).strip()
    matches = [entry for entry in history
               if isinstance(entry, dict) and str(entry.get('gup', '')).strip() == gup_str
               and entry.get('presentation_url')]

    if not matches:
        log.warning('No tomolog entry found for GUP %s in %s' % (gup_str, tomolog_path))
        return None

    matches.sort(key=lambda e: str(e.get('date', '')), reverse=True)
    url = matches[0]['presentation_url']
    log.info('Found presentation URL for GUP %s: %s' % (gup_str, url))
    return url
