import datetime
import os
import subprocess

from dmagic import log
from dmagic import authorize
from dmagic import scheduling
from dmagic import utils

__author__ = "Alan L Kastengren, Francesco De Carlo"
__copyright__ = "Copyright (c) 2020, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

try:
    from dm import ExperimentDsApi, UserDsApi, ExperimentDaqApi, EsafApsDbApi
    from dm.common.exceptions.objectAlreadyExists import ObjectAlreadyExists
    exp_api  = ExperimentDsApi()
    user_api = UserDsApi()
    daq_api  = ExperimentDaqApi()
    esaf_api = EsafApsDbApi()
    oee      = ObjectAlreadyExists
    _DM_AVAILABLE = True
except ImportError:
    exp_api = user_api = daq_api = esaf_api = oee = None
    _DM_AVAILABLE = False
    log.warning('DM SDK not available: create, delete, email, add-user, remove-user, daq-start, daq-stop commands will not work')


def get_esaf_users(esaf_id):
    """Return set of 'd+badge' strings for users listed in the ESAF.

    Uses EsafApsDbApi.getStationEsafById() with the station name from the
    DM_STATION_NAME environment variable (default '2BM').
    Returns an empty set if esaf_id is empty, DM is unavailable, or the
    call fails (e.g. session expired or access denied).
    """
    if not esaf_id or not _DM_AVAILABLE:
        return set()
    try:
        station = os.environ.get('DM_STATION_NAME', '2BM')
        esaf = esaf_api.getStationEsafById(station, int(esaf_id))
        users = esaf.get('experimentUsers', [])
        badges = {'d' + str(u['badge']) for u in users if u.get('badge')}
        log.info('   Found %d user(s) in ESAF %s' % (len(badges), esaf_id))
        return badges
    except Exception as e:
        log.warning('Could not retrieve ESAF users for ESAF %s: %s' % (esaf_id, str(e)))
        return set()


def get_esaf_doi(esaf_id):
    """Return the DOI string for the ESAF, or None if unavailable."""
    if not esaf_id or not _DM_AVAILABLE:
        return None
    try:
        station = os.environ.get('DM_STATION_NAME', '2BM')
        esaf = esaf_api.getStationEsafById(station, int(esaf_id))
        return esaf.get('doi') or None
    except Exception as e:
        log.warning('Could not retrieve DOI for ESAF %s: %s' % (esaf_id, str(e)))
        return None


def list_esafs(start_date, end_date, station=None):
    """Return ESAFs for the station in [start_date, end_date].

    Wraps EsafApsDbApi.listStationEsafsByDateRange(). Dates are YYYY-MM-DD
    strings. station defaults to DM_STATION_NAME env var (or '2BM').
    Returns [] if DM is unavailable or the call fails.
    """
    if not _DM_AVAILABLE:
        return []
    if station is None:
        station = os.environ.get('DM_STATION_NAME', '2BM')
    try:
        result = esaf_api.listStationEsafsByDateRange(
            station, startDate=start_date, endDate=end_date)
        return list(result) if result else []
    except Exception as e:
        log.error('Could not list ESAFs for station %s: %s' % (station, str(e)))
        return []


def make_experiment_name(args):
    """Build the DM experiment name from proposal metadata.

    Format: {year_month}-{pi_last_name}-{gup_number}
    Example: 2025-03-Smith-123456
    """
    pi_last_name = utils.clean_entry(args.pi_last_name)
    return '{:s}-{:s}-{:s}'.format(args.year_month, pi_last_name, str(args.gup_number))


def make_dm_username_list(args):
    """Make DM username sets from the proposal (GUP) and ESAF user lists.

    Returns (gup_set, esaf_set) where:
      gup_set  — 'd+badge' strings from proposal experimenters + beamline contacts
      esaf_set — 'd+badge' strings from ESAF experimenters NOT already in gup_set
    Returns (None, set()) if the beamtime cannot be found in the scheduling system.
    """
    log.info('Making a list of DM system usernames from target proposal')
    auth = authorize.basic(args.credentials)
    if auth is None:
        return None, set()
    target_prop = scheduling.get_beamtime(str(args.gup_number), auth, args)
    if target_prop is None:
        return None, set()
    users = target_prop['beamtime']['proposal']['experimenters']
    log.info('   Adding the primary beamline contact')
    gup_set = {'d' + str(args.primary_beamline_contact_badge)}
    log.info('   Adding the secondary beamline contact')
    gup_set.add('d' + str(args.secondary_beamline_contact_badge))
    for u in users:
        log.info('   Adding GUP user {0}, {1}, badge {2}'.format(
                    u['lastName'], u['firstName'], u['badge']))
        gup_set.add('d' + str(u['badge']))
    esaf_number = getattr(args, 'esaf_number', '') or ''
    esaf_set = get_esaf_users(esaf_number) - gup_set
    return gup_set, esaf_set


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
            log.warning('   User {:s} ({:s}) is already on the experiment'.format(
                        make_pretty_user_name(user_obj), uname))
            continue
        try:
            user_api.addUserExperimentRole(uname, 'User', exp_obj['name'])
            log.info('   Added user {:s} ({:s}) to the DM experiment'.format(
                        make_pretty_user_name(user_obj), uname))
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
            log.info('   Removed user {:s} ({:s}) from the DM experiment'.format(
                        make_pretty_user_name(user_obj), uname))
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


def get_emailed_users(exp_name):
    """Return the set of DM usernames already emailed for this experiment.

    Reads from DM experiment metadata key 'emailedUsers'. Returns an empty
    set if the metadata has not been set yet or on any error.
    """
    try:
        exp_obj = exp_api.getExperimentByName(exp_name)
        stored = exp_obj.get('emailedUsers', '')
        return set(u for u in stored.split(',') if u)
    except Exception:
        return set()


def set_emailed_users(exp_name, username_set):
    """Persist the set of emailed DM usernames as experiment metadata.

    Stores under key 'emailedUsers' as a comma-separated string.
    """
    value = ','.join(sorted(username_set))
    try:
        exp_api.upsertExperimentMetadata('emailedUsers', value, exp_name)
        log.info('   Updated emailed-users record for %s' % exp_name)
    except Exception as e:
        log.warning('   Could not save emailed-users metadata: %s' % str(e))


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

    Uses getExperimentsByStation(stationName=station). Sorted newest first
    by startDate, with experiment name as a secondary tiebreaker so
    experiments started on the same day (or in the same month, when
    startDate is missing) appear in a stable order run-to-run —
    getExperimentsByStation itself does not guarantee ordering.
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
        # Primary key: startDate descending (newest first). Secondary key:
        # experiment name ascending so ties within the same startDate — or
        # experiments without a startDate — still land in a stable order.
        # Sort by name first (ascending) then by startDate (descending);
        # Python's stable sort preserves the name order within a startDate.
        filtered.sort(key=lambda e: e.get('name', ''))
        filtered.sort(key=lambda e: e.get('startDate', '') or '', reverse=True)
        return filtered
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


def build_gup_experiment_index(station, years=3):
    """Return {gup_str: [experiment_obj, ...]} for DM experiments at station.

    Uses list_experiments_by_station (which itself caps at `years` calendar
    years back). GUP is parsed from the last '-'-separated field of the
    experiment name (matches the YYYY-MM-Lastname-GUP convention). Manual
    commissioning experiments with a trailing '-0' end up under key '0',
    which will never match a real beamtime GUP — that's the intended
    behaviour.
    """
    exps = list_experiments_by_station(station, years=years)
    index = {}
    for e in exps:
        name = e.get('name', '') or ''
        parts = name.rsplit('-', 1)
        if len(parts) == 2 and parts[1].isdigit():
            index.setdefault(parts[1], []).append(e)
    return index


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


def _inspect_local_source(local_path):
    """Look at a local source directory that DM would read from.

    Walks the tree recursively so a directory that contains only
    subfolders of files (typical for reconstruction output — each
    _rec/ scan is a folder of tiffs) is reported OK, not EMPTY.

    Returns (status, count, size_bytes) where status is one of:
      OK       - directory exists and has at least one file
                 (count = number of regular files at any depth,
                 size_bytes = sum of their sizes)
      EMPTY    - directory exists but has no files at any depth
      MISSING  - parent mount is visible but the directory is not there
                 (usually a misconfigured data-top-dir or exp-name)
      UNKNOWN  - parent mount is not visible from this host; caller
                 should try _inspect_remote_source before giving up.
    count and size_bytes are None for MISSING/UNKNOWN.
    """
    if os.path.isdir(local_path):
        count = 0
        total = 0
        try:
            for root, dirs, files in os.walk(local_path):
                for name in files:
                    try:
                        total += os.path.getsize(os.path.join(root, name))
                        count += 1
                    except OSError:
                        pass
        except OSError:
            return 'UNKNOWN', None, None
        if count == 0:
            return 'EMPTY', 0, 0
        return 'OK', count, total
    parent = os.path.dirname(local_path.rstrip('/'))
    if parent and os.path.isdir(parent):
        return 'MISSING', None, None
    return 'UNKNOWN', None, None


_ssh_warned = set()  # hosts we've already emitted the setup warning for


def _warn_ssh_setup(host, reason):
    """Emit an actionable warning explaining how to enable passwordless
    SSH so future dmagic runs get the source pre-check. Once per host
    per process — we don't want to spam the same 6 lines for raw+rec.
    """
    if host in _ssh_warned:
        return
    _ssh_warned.add(host)
    log.warning('Cannot SSH-check source on %s (%s).' % (host, reason))
    log.warning('To enable dmagic to pre-check the source directory,')
    log.warning('set up passwordless SSH from this host to %s once:' % host)
    log.warning("    ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519   # if you have no key yet")
    log.warning('    ssh-copy-id %s' % host)
    log.warning('    ssh -o BatchMode=yes %s "echo ok"                 # verify' % host)
    log.warning('Continuing without pre-check; verify destination after transfer.')


def _inspect_remote_source(host, path, timeout=5):
    """Same as _inspect_local_source, but over SSH to `host`.

    Uses BatchMode so it never prompts; if SSH is unusable (no key, host
    unreachable, timeout) we log an actionable warning (once per host)
    and return UNKNOWN so DM dispatches as before.
    """
    # Once we're SSH-connected we can distinguish three failure modes:
    #   MISSING     - experiment dir missing, but data-top-dir exists
    #   NO_TOPDIR   - data-top-dir itself does not exist on the host
    #                 (usually the wrong --data-host or --data-top-dir)
    # Never emit UNKNOWN from a successful SSH: we know what's on the host.
    # Count files recursively (any depth) so a dir whose top-level
    # entries are all subdirectories — typical for reconstruction
    # output (_rec/ containing 10_000_rec/, 10_001_rec/, try_center/) —
    # is reported OK, not EMPTY. Matches _inspect_local_source semantics.
    script = (
        'p=%(p)s; '
        'if [ -d "$p" ]; then '
        '  n=$(find "$p" -type f 2>/dev/null | wc -l); '
        '  b=$(du -sb "$p" 2>/dev/null | cut -f1); '
        '  [ "$n" = "0" ] && echo EMPTY || echo "OK $n $b"; '
        'elif [ -d "$(dirname "$p")" ]; then echo MISSING; '
        'else echo "NO_TOPDIR $(dirname "$p")"; fi'
    ) % {'p': _shquote(path)}
    try:
        r = subprocess.run(
            ['ssh', '-o', 'BatchMode=yes',
             '-o', 'ConnectTimeout=%d' % timeout,
             '-o', 'StrictHostKeyChecking=accept-new',
             host, script],
            capture_output=True, text=True, timeout=timeout + 10)
    except Exception as e:
        _warn_ssh_setup(host, str(e))
        return 'UNKNOWN', None, None
    if r.returncode != 0:
        err = (r.stderr or '').strip().splitlines()
        _warn_ssh_setup(host, err[-1] if err else 'ssh exit %d' % r.returncode)
        return 'UNKNOWN', None, None
    out = (r.stdout or '').strip()
    if not out:
        _warn_ssh_setup(host, 'empty response from remote probe')
        return 'UNKNOWN', None, None
    if out in ('EMPTY', 'MISSING'):
        return out, (0 if out == 'EMPTY' else None), (0 if out == 'EMPTY' else None)
    parts = out.split()
    if len(parts) == 3 and parts[0] == 'OK':
        try:
            return 'OK', int(parts[1]), int(parts[2])
        except ValueError:
            return 'UNKNOWN', None, None
    if len(parts) >= 2 and parts[0] == 'NO_TOPDIR':
        # size_bytes carries the missing parent path so _report_source can name it
        return 'NO_TOPDIR', None, ' '.join(parts[1:])
    return 'UNKNOWN', None, None


def _shquote(s):
    """Minimal single-quote shell escaping for a path argument."""
    return "'" + s.replace("'", "'\\''") + "'"


def _inspect_source(host, path):
    """Inspect a source dir on `host` at `path`.

    Try locally first (works when the data mount is visible from the
    machine running dmagic — beamline-node case). Fall back to SSH into
    `host` when local returns UNKNOWN (control-computer case, e.g.
    arcturus, which does not mount /data2 or /data3).
    """
    status, n, sz = _inspect_local_source(path)
    if status != 'UNKNOWN':
        return status, n, sz
    return _inspect_remote_source(host, path)


def _report_source(local_path, host, status, count, size_bytes, role):
    """Log what _inspect_source found. role is 'raw' or 'rec'.

    `host` is the data-host value used for the inspection — included in
    MISSING / NO_TOPDIR messages so users see immediately which host
    was probed.

    Missing raw is an error (dmagic is misconfigured); missing rec is a
    warning (recon may not have run yet). Returns True if the caller
    should proceed with the DM dispatch, False if it should skip.
    """
    fix_hint = ('Check data-host / data-top-dir in ~/dmagic.conf, or pass '
                '--data-host / --data-top-dir on the CLI. DM would silently '
                'transfer nothing. Skipping.')

    if status == 'OK':
        log.info('   Source has %d file(s), %.2f GiB'
                 % (count, size_bytes / (1024.0 ** 3)))
        return True
    if status == 'EMPTY':
        log.warning('   Source %s is empty; DM will transfer 0 files' % local_path)
        return True
    if status == 'MISSING':
        if role == 'raw':
            log.error('   Source %s does not exist on data-host=%s.'
                      % (local_path, host))
            log.error('   %s' % fix_hint)
        else:
            log.warning('   Source %s does not exist on data-host=%s yet'
                        ' (recon may not have run). Skipping.'
                        % (local_path, host))
        return False
    if status == 'NO_TOPDIR':
        # size_bytes was repurposed to carry the missing parent path
        missing_parent = size_bytes or 'data-top-dir'
        log.error('   Data top directory %s does not exist on data-host=%s.'
                  % (missing_parent, host))
        log.error('   %s' % fix_hint)
        return False
    log.info('   Source path not visible from this host (no local mount); '
             'proceeding without pre-check')
    return True


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


def _dm_data_dir(data_host, local_path, dm_direct_mount):
    """Format the dataDirectory URL for daq_api calls.

    When dm_direct_mount is True the DM VM already mounts the source
    filesystem directly, so we pass the bare local path. Otherwise we
    prepend @{data-host}: for the remote-rsync syntax.
    """
    if dm_direct_mount:
        return local_path
    return '@{:s}:{:s}'.format(data_host, local_path)


def start_daq(exp_name, data_host, data_top_dir, dm_direct_mount=False):
    """Start two DM DAQs for exp_name:
      - raw data:          data_top_dir/<exp_name>      → DM data directory
      - reconstructed data: data_top_dir/<exp_name>_rec → DM analysis directory

    The rec DAQ is skipped with a warning if the directory does not yet exist.
    If dm_direct_mount is True, the source URL passed to DM is the bare local
    path; otherwise it is prefixed with @{data-host}:. Returns True if at least
    the raw DAQ started, False on error.
    """
    log.info('Checking for already running DAQs for experiment %s' % exp_name)
    try:
        current_daqs = daq_api.listDaqs()
    except Exception as e:
        log.error('   Could not list DAQs: %s' % str(e))
        return False

    top = data_top_dir.rstrip('/')

    raw_local = os.path.join(top, exp_name)
    rec_local = os.path.join(top, exp_name + '_rec')

    # Raw data DAQ → DM data directory
    raw_dir = _dm_data_dir(data_host, raw_local, dm_direct_mount)
    log.info('Starting raw data DAQ for experiment %s' % exp_name)
    log.info('   Source: %s' % raw_dir)
    raw_status, raw_n, raw_sz = _inspect_source(data_host, raw_local)
    if not _report_source(raw_local, data_host, raw_status, raw_n, raw_sz, role='raw'):
        return False
    raw_ok = _start_one_daq(exp_name, raw_dir, {'processExistingFiles': True}, current_daqs)

    # Reconstructed data DAQ → DM analysis directory
    rec_dir = _dm_data_dir(data_host, rec_local, dm_direct_mount)
    log.info('Starting reconstructed data DAQ for experiment %s' % exp_name)
    log.info('   Source: %s' % rec_dir)
    rec_status, rec_n, rec_sz = _inspect_source(data_host, rec_local)
    rec_ok = False
    if _report_source(rec_local, data_host, rec_status, rec_n, rec_sz, role='rec'):
        rec_ok = _start_one_daq(exp_name, rec_dir, {'useAnalysisDirectoryAsRoot': True, 'processExistingFiles': True}, current_daqs)
    if not rec_ok:
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


def list_running_daqs(station):
    """Return all currently running DM DAQs for the given station.

    Filters daq_api.listDaqs() to entries with status='running' and
    experimentStationName matching the given station (e.g. '2BM').
    Returns [] on API error or if none are running.
    """
    try:
        all_daqs = daq_api.listDaqs()
    except Exception as e:
        log.error('   Could not list DAQs: %s' % str(e))
        return []
    return [d for d in all_daqs
            if d.get('status') == 'running'
            and d.get('experimentStationName') == station]


def upload(exp_name, data_host, data_top_dir, dm_direct_mount=False):
    """One-shot upload of raw and reconstructed data to the DM experiment.

    Uploads files that exist at the time the command is issued (unlike DAQ,
    which monitors for new files continuously). Use this when daq-start was
    not running while data was being collected. Uses the same source directories
    as daq-start:

      - raw data:           data_top_dir/<exp_name>      → DM data directory
      - reconstructed data: data_top_dir/<exp_name>_rec  → DM analysis directory

    The rec upload is skipped with a warning if the directory does not exist.
    If dm_direct_mount is True, the source URL passed to DM is the bare local
    path; otherwise it is prefixed with @{data-host}:. Returns True if at
    least the raw upload started, False on error.
    """
    top = data_top_dir.rstrip('/')

    raw_local = os.path.join(top, exp_name)
    rec_local = os.path.join(top, exp_name + '_rec')
    raw_dir = _dm_data_dir(data_host, raw_local, dm_direct_mount)
    rec_dir = _dm_data_dir(data_host, rec_local, dm_direct_mount)

    # Raw data → DM data directory
    log.info('Uploading raw data for experiment %s' % exp_name)
    log.info('   Source: %s' % raw_dir)
    raw_ok = False
    raw_status, raw_n, raw_sz = _inspect_source(data_host, raw_local)
    if _report_source(raw_local, data_host, raw_status, raw_n, raw_sz, role='raw'):
        try:
            daq_api.upload(exp_name, raw_dir)
            log.info('   Raw data upload dispatched to DM')
            raw_ok = True
        except Exception as e:
            log.error('   Could not start raw data upload: %s' % str(e))

    # Reconstructed data → DM analysis directory
    log.info('Uploading reconstructed data for experiment %s' % exp_name)
    log.info('   Source: %s' % rec_dir)
    rec_status, rec_n, rec_sz = _inspect_source(data_host, rec_local)
    if _report_source(rec_local, data_host, rec_status, rec_n, rec_sz, role='rec'):
        try:
            daq_api.upload(exp_name, rec_dir, {'useAnalysisDirectoryAsRoot': True})
            log.info('   Reconstructed data upload dispatched to DM')
        except Exception as e:
            log.warning('   Could not start reconstructed data upload: %s' % str(e))

    return raw_ok
