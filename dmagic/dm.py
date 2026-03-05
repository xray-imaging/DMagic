import datetime

from dm import ExperimentDsApi, UserDsApi
from dm.common.exceptions.objectAlreadyExists import ObjectAlreadyExists

from dmagic import log
from dmagic import authorize
from dmagic import scheduling
from dmagic import utils

__author__ = "Alan L Kastengren, Francesco De Carlo"
__copyright__ = "Copyright (c) 2020, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

exp_api  = ExperimentDsApi()
user_api = UserDsApi()
oee      = ObjectAlreadyExists


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

    if args.manual:
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


def list_users_this_dm_exp(args):
    """Return the list of DM usernames on the current experiment, or None if not found."""
    log.info('Listing the users on the DM experiment')
    exp_name = make_experiment_name(args)
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


def get_experiment(exp_name):
    """Return the DM experiment object for exp_name, or None if not found."""
    try:
        return exp_api.getExperimentByName(exp_name)
    except Exception as e:
        if 'does not exist' in str(e):
            return None
        log.error('Could not query DM experiment %s: %s' % (exp_name, str(e)))
        return None


def delete_experiment(args):
    """Delete a DM experiment from Sojourner by name.

    Returns True on success, False on error.
    """
    exp_name = make_experiment_name(args)
    log.info('Deleting DM experiment: %s' % exp_name)
    try:
        exp_api.deleteExperiment(exp_name)
        log.info('   Experiment %s successfully deleted' % exp_name)
        return True
    except Exception as e:
        log.error('   Could not delete experiment %s: %s' % (exp_name, str(e)))
        return False


def make_data_link(args):
    """Build the Globus file-manager URL for the experiment data directory."""
    exp_name = make_experiment_name(args)
    target_dir = '/{:s}/{:s}/'.format(args.year_month, exp_name)
    link = ('https://app.globus.org/file-manager?origin_id='
            + args.globus_server_uuid
            + '&origin_path='
            + target_dir.replace('/', '%2F'))
    return link
