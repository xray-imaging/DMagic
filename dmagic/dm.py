import datetime
import os

from dmagic import log
from dmagic import authorize
from dmagic import scheduling
from dmagic import utils

__author__ = "Alan L Kastengren, Francesco De Carlo"
__copyright__ = "Copyright (c) 2020, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

try:
    from dm import ExperimentDsApi, UserDsApi, ExperimentDaqApi
    from dm.common.exceptions.objectAlreadyExists import ObjectAlreadyExists
    exp_api  = ExperimentDsApi()
    user_api = UserDsApi()
    daq_api  = ExperimentDaqApi()
    oee      = ObjectAlreadyExists
    _DM_AVAILABLE = True
except ImportError:
    exp_api = user_api = daq_api = oee = None
    _DM_AVAILABLE = False
    log.warning('DM SDK not available: create, delete, email, add-user, remove-user, daq-start, daq-stop commands will not work')


def make_experiment_name(args):
    """Build the DM experiment name from proposal metadata.

    Format: {year_month}-{pi_last_name}-{gup_number}
    Example: 2025-03-Smith-123456
    """
    pi_last_name = utils.clean_entry(args.pi_last_name)
    return '{:s}-{:s}-{:s}'.format(args.year_month, pi_last_name, str(args.gup_number))


def make_dm_username_list(args):
    """Make a list of DM usernames 'd+badge#' from the current proposal (GUP number).

    Returns None if the beamtime cannot be found in the scheduling system.
    """
    log.info('Making a list of DM system usernames from target proposal')
    auth = authorize.basic(args.credentials)
    if auth is None:
        return None
    target_prop = scheduling.get_beamtime(str(args.gup_number), auth, args)
    if target_prop is None:
        return None
    users = target_prop['beamtime']['proposal']['experimenters']
    log.info('   Adding the primary beamline contact')
    user_ids = {'d' + str(args.primary_beamline_contact_badge)}
    log.info('   Adding the secondary beamline contact')
    user_ids.add('d' + str(args.secondary_beamline_contact_badge))
    for u in users:
        log.info('   Adding user {0}, {1}, badge {2}'.format(
                    u['lastName'], u['firstName'], u['badge']))
        user_ids.add('d' + str(u['badge']))
    return user_ids


def make_username_list(args):
    """Return the list of DM usernames currently on the experiment."""
    log.info('Making a list of DM system usernames from current DM experiment')
    exp_name = make_experiment_name(args)
    try:
        exp_obj = exp_api.getExperimentByName(exp_name)
        return exp_obj.get('experimentUsernameList', [])
    except Exception as e:
        log.error('No such experiment in the DM system: {:s}'.format(exp_name))
        log.error('   Error: %s' % str(e))
        log.error('   Have you run "dmagic create" yet?')
        return []


def make_user_email_list(username_list):
    """Convert a list of DM usernames ('d+badge#') to email addresses."""
    email_list = []
    for u in username_list:
        try:
            user_obj = user_api.getUserByUsername(u)
            email_list.append(user_obj['email'])
            log.info('   Added email {:s} for user {:s}'.format(email_list[-1], u))
        except Exception as e:
            log.warning('   Problem loading email for user {:s}: {:s}'.format(u, str(e)))
    return email_list


def create_experiment(args):
    """Create a new DM experiment on Sojourner.

    Returns the experiment object (new or pre-existing), or None on error.
    """
    exp_name = make_experiment_name(args)
    log.info('Checking for existing DM experiment')
    try:
        old_exp = exp_api.getExperimentByName(exp_name)
        log.warning('   Experiment already exists: %s' % old_exp['name'])
        return old_exp
    except Exception as e:
        error_msg = str(e)
        if 'does not exist' in error_msg:
            log.info('   Experiment does not exist yet, will create it')
        else:
            log.error('   Could not query DM system: %s' % error_msg)
            return None

    log.info('Creating new DM experiment: {0:s}/{1:s}'.format(args.year_month, exp_name))

    if getattr(args, 'manual', False):
        start_date = args.manual_start
        end_date   = args.manual_end
    else:
        auth = authorize.basic(args.credentials)
        if auth is None:
            return None
        target_beamtime = scheduling.get_beamtime(args.gup_number, auth, args)
        if target_beamtime is None:
            log.error('  Could not find beamtime for GUP %s. '
                      'For a commissioning run with no proposal use: '
                      '"dmagic create --manual --name <LastName> '
                      '--title <Title> --badges <badge1,badge2,...>"'
                      % args.gup_number)
            return None
        start_datetime = datetime.datetime.strptime(
                            utils.fix_iso(target_beamtime['startTime']),
                            '%Y-%m-%dT%H:%M:%S%z')
        end_datetime = datetime.datetime.strptime(
                            utils.fix_iso(target_beamtime['endTime']),
                            '%Y-%m-%dT%H:%M:%S%z')
        start_date = start_datetime.strftime('%d-%b-%y')
        end_date   = end_datetime.strftime('%d-%b-%y')

    try:
        new_exp = exp_api.addExperiment(exp_name,
                            typeName    = args.experiment_type,
                            description = args.gup_title,
                            rootPath    = args.year_month,
                            startDate   = start_date,
                            endDate     = end_date)
        log.info('   Experiment successfully created: %s' % new_exp['name'])
        return new_exp
    except oee:
        log.warning('   Experiment already exists (caught on create). Retrieving: %s' % exp_name)
        return exp_api.getExperimentByName(exp_name)
    except Exception as e:
        log.error('   Could not create DM experiment: %s' % str(e))
        return None


def add_users(exp_obj, username_list):
    """Add a list of DM usernames to an experiment."""
    existing_unames = exp_obj.get('experimentUsernameList', [])
    for uname in username_list:
        try:
            user_obj = user_api.getUserByUsername(uname)
        except Exception as e:
            log.error('   Could not find user {:s}: {:s}'.format(uname, str(e)))
            continue
        if uname in existing_unames:
            log.warning('   User {:s} is already on the experiment'.format(
                        make_pretty_user_name(user_obj)))
            continue
        try:
            user_api.addUserExperimentRole(uname, 'User', exp_obj['name'])
            log.info('   Added user {:s} to the DM experiment'.format(
                        make_pretty_user_name(user_obj)))
        except Exception as e:
            log.error('   Could not add user {:s}: {:s}'.format(uname, str(e)))


def remove_users(exp_name, username_list):
    """Remove a list of DM usernames from an experiment."""
    for uname in username_list:
        try:
            user_obj = user_api.getUserByUsername(uname)
        except Exception as e:
            log.error('   Could not find user {:s}: {:s}'.format(uname, str(e)))
            continue
        try:
            user_api.deleteUserExperimentRole(uname, 'User', exp_name)
            log.info('   Removed user {:s} from the DM experiment'.format(
                        make_pretty_user_name(user_obj)))
        except Exception as e:
            log.error('   Could not remove user {:s}: {:s}'.format(uname, str(e)))


def list_users_this_dm_exp(args):
    """Return the list of DM usernames on the current experiment, or None if not found."""
    log.info('Listing the users on the DM experiment')
    exp_name = getattr(args, '_exp_name', None) or make_experiment_name(args)
    try:
        exp_obj = exp_api.getExperimentByName(exp_name)
    except Exception as e:
        log.error('   No appropriate DM experiment found: %s' % str(e))
        return None
    username_list = exp_obj.get('experimentUsernameList', [])
    if not username_list:
        log.info('   No users for this experiment')
        return None
    return username_list


def make_pretty_user_name(user_obj):
    """Format a DM user object as 'FirstName MiddleName LastName'."""
    parts = []
    for key in ('firstName', 'middleName', 'lastName'):
        if key in user_obj and user_obj[key]:
            parts.append(user_obj[key])
    return ' '.join(parts)


def get_user(username):
    """Return the DM user object for a username, or None on error."""
    try:
        return user_api.getUserByUsername(username)
    except Exception:
        return None


def get_experiment(exp_name):
    """Return the DM experiment object for exp_name, or None if not found."""
    try:
        return exp_api.getExperimentByName(exp_name)
    except Exception as e:
        if 'does not exist' in str(e):
            return None
        log.error('Could not query DM experiment %s: %s' % (exp_name, str(e)))
        return None


def list_experiments_by_station(station, years=2):
    """Return DM experiment objects for the station from the last `years` calendar years.

    Uses getExperimentsByStation(stationName=station). Sorted newest first.
    Returns [] on error or no results.
    """
    try:
        result = exp_api.getExperimentsByStation(stationName=station)
        if not result:
            return []
        exps = list(result) if isinstance(result, list) else list(result.values())
        cutoff_year = datetime.datetime.now().year - years + 1
        filtered = []
        for e in exps:
            try:
                year = int(e.get('rootPath', '0').split('-')[0])
                if year >= cutoff_year:
                    filtered.append(e)
            except (ValueError, IndexError):
                pass
        return sorted(filtered, key=lambda e: e.get('rootPath', ''), reverse=True)
    except Exception as e:
        error_msg = str(e)
        log.error('Could not list DM experiments for station %s: %s' % (station, error_msg))
        if 'incorrect username or password' in error_msg.lower():
            import os
            login_file = os.environ.get('DM_LOGIN_FILE', 'not set')
            log.error('   DM authentication failed. Check that DM_LOGIN_FILE is accessible.')
            log.error('   DM_LOGIN_FILE = %s' % login_file)
            if login_file != 'not set' and not os.path.isfile(login_file):
                log.error('   File not found — this machine may not have the required NFS mount.')
                log.error('   Run DM commands from a beamline control machine (e.g. arcturus).')
        return []


def delete_experiment(exp_name):
    """Delete a DM experiment from Sojourner by name.

    Returns True on success, False on error.
    """
    log.info('Deleting DM experiment: %s' % exp_name)
    try:
        exp_api.deleteExperimentByName(exp_name)
        log.info('   Experiment %s successfully deleted' % exp_name)
        return True
    except Exception as e:
        log.error('   Could not delete experiment %s: %s' % (exp_name, str(e)))
        return False


def make_data_link(args):
    """Build the Globus file-manager URL for the experiment data directory."""
    exp_name   = getattr(args, '_exp_name',   None) or make_experiment_name(args)
    year_month = getattr(args, '_year_month',  None) or args.year_month
    target_dir = '/{:s}/{:s}/'.format(year_month, exp_name)
    link = ('https://app.globus.org/file-manager?origin_id='
            + args.globus_server_uuid
            + '&origin_path='
            + target_dir.replace('/', '%2F'))
    return link


def _start_one_daq(exp_name, dm_dir_name, task_info, current_daqs):
    """Start a single DAQ if not already running for (exp_name, dm_dir_name).

    Returns True if already running or successfully started, False on error.
    """
    for d in current_daqs:
        if (d['experimentName'] == exp_name and d['status'] == 'running'
                and d['dataDirectory'] == dm_dir_name):
            log.warning('   DAQ already running for %s' % dm_dir_name)
            return True
    log.info('   Watching directory: %s' % dm_dir_name)
    try:
        daq_api.startDaq(exp_name, dm_dir_name, task_info)
        log.info('   DAQ started successfully')
        return True
    except Exception as e:
        log.error('   Could not start DAQ: %s' % str(e))
        return False


def start_daq(exp_name, analysis, analysis_top_dir):
    """Start two DM DAQs for exp_name:
      - raw data:          analysis_top_dir/<exp_name>      → DM data directory
      - reconstructed data: analysis_top_dir/<exp_name>_rec → DM analysis directory

    The rec DAQ is skipped with a warning if the directory does not yet exist.
    Returns True if at least the raw DAQ started, False on error.
    """
    log.info('Checking for already running DAQs for experiment %s' % exp_name)
    try:
        current_daqs = daq_api.listDaqs()
    except Exception as e:
        log.error('   Could not list DAQs: %s' % str(e))
        return False

    top = analysis_top_dir.rstrip('/')

    # Raw data DAQ → DM data directory
    raw_dir = '@{:s}:{:s}'.format(analysis, os.path.join(top, exp_name))
    log.info('Starting raw data DAQ for experiment %s' % exp_name)
    raw_ok = _start_one_daq(exp_name, raw_dir, {}, current_daqs)

    # Reconstructed data DAQ → DM analysis directory
    rec_dir = '@{:s}:{:s}'.format(analysis, os.path.join(top, exp_name + '_rec'))
    log.info('Starting reconstructed data DAQ for experiment %s' % exp_name)
    rec_ok = _start_one_daq(exp_name, rec_dir, {'useAnalysisDirectory': True}, current_daqs)
    if not rec_ok:
        log.warning('   Rec DAQ could not be started (directory may not exist yet)')
        log.warning('   Run "dmagic daq-start" again once reconstruction begins')

    return raw_ok


def stop_daq(exp_name):
    """Stop all running DM DAQs for exp_name.

    Returns True on success (including no DAQs found), False on error.
    """
    log.info('Stopping all DM DAQs for experiment %s' % exp_name)
    try:
        daqs = daq_api.listDaqs()
    except Exception as e:
        log.error('   Could not list DAQs: %s' % str(e))
        return False

    count = 0
    for d in daqs:
        if d['experimentName'] == exp_name and d['status'] == 'running':
            log.info('   Found running DAQ. Stopping now.')
            try:
                daq_api.stopDaq(d['experimentName'], d['dataDirectory'])
                count += 1
            except Exception as e:
                log.error('   Could not stop DAQ: %s' % str(e))

    if count == 0:
        log.info('   No active DAQs found for experiment %s' % exp_name)
    else:
        log.info('   Stopped %d DAQ(s) for experiment %s' % (count, exp_name))
    return True


def upload(exp_name, analysis, analysis_top_dir):
    """One-shot upload of raw and reconstructed data to the DM experiment.

    Uploads files that exist at the time the command is issued (unlike DAQ,
    which monitors for new files continuously). Use this when daq-start was
    not running while data was being collected. Uses the same source directories
    as daq-start:

      - raw data:           analysis_top_dir/<exp_name>      → DM data directory
      - reconstructed data: analysis_top_dir/<exp_name>_rec  → DM analysis directory

    The rec upload is skipped with a warning if the directory does not exist.
    Returns True if at least the raw upload started, False on error.
    """
    top = analysis_top_dir.rstrip('/')

    raw_dir = '@{:s}:{:s}'.format(analysis, os.path.join(top, exp_name))
    rec_dir = '@{:s}:{:s}'.format(analysis, os.path.join(top, exp_name + '_rec'))

    # Raw data → DM data directory
    log.info('Uploading raw data for experiment %s' % exp_name)
    log.info('   Source: %s' % raw_dir)
    raw_ok = False
    try:
        daq_api.upload(exp_name, raw_dir)
        log.info('   Raw data upload started successfully')
        raw_ok = True
    except Exception as e:
        log.error('   Could not start raw data upload: %s' % str(e))

    # Reconstructed data → DM analysis directory
    log.info('Uploading reconstructed data for experiment %s' % exp_name)
    log.info('   Source: %s' % rec_dir)
    try:
        daq_api.upload(exp_name, rec_dir, {'useAnalysisDirectory': True})
        log.info('   Reconstructed data upload started successfully')
    except Exception as e:
        log.warning('   Could not start reconstructed data upload: %s' % str(e))
        log.warning('   (directory may not exist yet)')

    return raw_ok
