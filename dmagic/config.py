import os
import sys
import pathlib
import argparse
import configparser
import numpy as np
from collections import OrderedDict
from dmagic import log

__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015-2016, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['config_to_list',
           'get_config_name',
           'log_values',
           'parse_known_args',
           'write']

CONFIG_FILE_NAME = os.path.join(str(pathlib.Path.home()), 'dmagic.conf')
CREDENTIALS_FILE_NAME = os.path.join(str(pathlib.Path.home()), '.scheduling_credentials')

SECTIONS = OrderedDict()

SECTIONS['general'] = {
    'config': {
        'default': CONFIG_FILE_NAME,
        'type': str,
        'help': "File name of configuration",
        'metavar': 'FILE'}}


SECTIONS['settings'] = {
    'set': {
        'type': float,
        'default': 0,
        'help': "Number of +/- days offset from today for past/future user groups"},
    }

SECTIONS['site'] = {
    'beamline': {
        'default': '2-BM-A,B',
        'type': str,
        'help': "Beamline name, e.g. 2-BM-A,B or 7-BM-B or 32-ID-B,C"},
    'credentials': {
        'default': CREDENTIALS_FILE_NAME,
        'type': str,
        'help': "File with scheduling REST API credentials in user|pwd format",
        'metavar': 'FILE'},
    'experiment-type': {
        'type': str,
        'default': '2BM',
        'help': 'Experiment type in the DM system'},
    'globus-message-file': {
        'type': str,
        'default': 'message-2bm.txt',
        'help': 'Email message template file name sent to users'},
    'globus-server-top-dir': {
        'type': str,
        'default': '/gdata/dm/2BM',
        'help': 'Path from data storage root to the beamline top directory'},
    'globus-server-uuid': {
        'type': str,
        'default': '054a0877-97ca-4d80-947f-47ca522b173e',
        'help': 'UUID of the Globus endpoint for the data management server (Sojourner)'},
    'primary-beamline-contact-badge': {
        'type': int,
        'default': 218262,
        'help': 'Badge number of primary beamline contact'},
    'primary-beamline-contact-email': {
        'type': str,
        'default': 'pshevchenko@anl.gov',
        'help': 'Email address of primary beamline contact'},
    'secondary-beamline-contact-badge': {
        'type': int,
        'default': 49734,
        'help': 'Badge number of secondary beamline contact'},
    'secondary-beamline-contact-email': {
        'type': str,
        'default': 'decarlo@anl.gov',
        'help': 'Email address of secondary beamline contact'},
    'tomolog-home': {
        'default': '/home/beams/TOMO',
        'type': str,
        'help': "Home directory of the account running tomolog; .tomolog history file is read from here"},
    'tomoscan-prefix': {
        'default': '2bmb:TomoScan:',
        'type': str,
        'help': "TomoScan EPICS IOC prefix, e.g. '2bmb:TomoScan:'"},
    'url': {
        'default': 'https://beam-api.aps.anl.gov',
        'type': str,
        'help': "URL of the scheduling system REST API"},
    'verbose': {
        'default': True,
        'help': 'Verbose output',
        'action': 'store_true'},
    }

SECTIONS['manual'] = {
    'badges': {
        'type': str,
        'default': '',
        'help': 'Comma-separated badge numbers to add to the experiment'},
    'date': {
        'type': str,
        'default': '',
        'help': 'Year-month in yyyy-mm format (default: current month)'},
    'email': {
        'type': str,
        'default': '',
        'help': 'PI email address'},
    'first-name': {
        'type': str,
        'default': '',
        'help': 'PI first name'},
    'institution': {
        'type': str,
        'default': '',
        'help': 'PI institution'},
    'name': {
        'type': str,
        'default': 'Staff',
        'help': 'PI last name'},
    'title': {
        'type': str,
        'default': 'Commissioning',
        'help': 'Experiment title'},
    }

SECTIONS['local'] = {
    'analysis': {
        'type': str,
        'default': 'tomodata3',
        'help': 'Hostname of the data analysis computer'},
    'analysis-top-dir': {
        'type': str,
        'default': '/data3/2BM/',
        'help': 'Top-level data directory on the analysis computer'},
    }

INIT_PARAMS   = ('site',)
SHOW_PARAMS   = ('settings',)
TAG_PARAMS    = ('settings',)
CREATE_PARAMS = ('settings',)
MANUAL_PARAMS = ('manual',)
EMAIL_PARAMS  = ()
DAQ_PARAMS    = ('local',)
SITE_SUPPRESS = ('site',)
NICE_NAMES    = ('General', 'Settings', 'Site', 'Manual', 'Local')
# Note: 'General' section only contains --config which is not logged


def get_config_name():
    """Get the command line --config option."""
    name = CONFIG_FILE_NAME
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--config'):
            if arg == '--config':
                return sys.argv[i + 1]
            else:
                name = sys.argv[i].split('--config')[1]
                if name[0] == '=':
                    name = name[1:]
                return name

    return name


def parse_known_args(parser, subparser=False):
    """
    Parse arguments from file and then override by the ones specified on the
    command line. Use *parser* for parsing and is *subparser* is True take into
    account that there is a value on the command line specifying the subparser.
    """
    if len(sys.argv) > 1:
        subparser_value = [sys.argv[1]] if subparser else []
        config_values = config_to_list(config_name=get_config_name())
        values = subparser_value + config_values + sys.argv[1:]
    else:
        values = ""

    return parser.parse_known_args(values)[0]


def config_to_list(config_name=CONFIG_FILE_NAME):
    """
    Read arguments from config file and convert them to a list of keys and
    values as sys.argv does when they are specified on the command line.
    *config_name* is the file name of the config file.
    """
    result = []
    config = configparser.ConfigParser()

    if not config.read([config_name]):
        return []

    for section in SECTIONS:
        for name, opts in ((n, o) for n, o in SECTIONS[section].items() if config.has_option(section, n)):
            value = config.get(section, name)

            if value != '' and value != 'None':
                action = opts.get('action', None)

                if action == 'store_true' and value == 'True':
                    # Only the key is on the command line for this action
                    result.append('--{}'.format(name))

                if not action == 'store_true':
                    if opts.get('nargs', None) == '+':
                        result.append('--{}'.format(name))
                        result.extend((v.strip() for v in value.split(',')))
                    else:
                        result.append('--{}={}'.format(name, value))

    return result


class Params(object):
    def __init__(self, sections=(), suppress_sections=()):
        self.sections = sections + ('general',)
        self.suppress_sections = suppress_sections

    def add_parser_args(self, parser):
        for section in self.sections:
            for name in sorted(SECTIONS[section]):
                opts = SECTIONS[section][name]
                parser.add_argument('--{}'.format(name), **opts)
        for section in self.suppress_sections:
            for name in sorted(SECTIONS[section]):
                opts = dict(SECTIONS[section][name])
                opts['help'] = argparse.SUPPRESS
                parser.add_argument('--{}'.format(name), **opts)

    def add_arguments(self, parser):
        self.add_parser_args(parser)
        return parser

    def get_defaults(self):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)

        return parser.parse_args('')


def write(config_file, args=None, sections=None):
    """
    Write *config_file* with values from *args* if they are specified,
    otherwise use the defaults. If *sections* are specified, write values from
    *args* only to those sections, use the defaults on the remaining ones.
    """
    config = configparser.ConfigParser()

    for section in SECTIONS:
        config.add_section(section)
        for name, opts in SECTIONS[section].items():
            if args and sections and section in sections and hasattr(args, name.replace('-', '_')):
                value = getattr(args, name.replace('-', '_'))
                if isinstance(value, list):
                    print(type(value), value)
                    value = ', '.join(value)
            else:
                value = opts['default'] if opts['default'] is not None else ''

            prefix = '# ' if value == '' else ''

            if name != 'config':
                config.set(section, prefix + name, str(value))
    with open(config_file, 'w') as f:
        config.write(f)


def log_values(args):
    """Log all values set in the args namespace.

    Arguments are grouped according to their section and logged alphabetically
    using the DEBUG log level thus --verbose is required.
    """
    args = args.__dict__

    for section, name in zip(SECTIONS, NICE_NAMES):
        entries = sorted((k for k in args.keys() if k.replace('_', '-') in SECTIONS[section]))

        if entries:
            log.info(name)

            for entry in entries:
                value = args[entry] if args[entry] is not None else "-"
                log.info("  {:<16} {}".format(entry, value))
