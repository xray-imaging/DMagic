#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright (c) 2015, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2015. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

"""
Module containing an example on how to use DMagic to access the APS scheduling
system information.

"""

import os
import sys
import time
import datetime
import zoneinfo
import argparse
import datetime as dt

from epics import PV

from dmagic import scheduling
from dmagic import log
from dmagic import config
from dmagic import authorize
from dmagic import utils
from dmagic import dm
from dmagic import message
from dmagic import tomolog as tomolog_utils


def init_PVs(args):
    """
    Initialize the EPICS PVs that will hold user and experiment information

    Parameters
    ----------
    args.tomoscan_prefix : EPICS IOC prefix, e.g. 2bma:TomoScan:

    Returns
    -------
    user_pvs : dict
        A dictionary of EPICS PVs
    """
    
    user_pvs = {}
    tomoscan_prefix = args.tomoscan_prefix
    log.info("Trying to initiale EPICS PVs")
    user_pvs['pi_name'] = PV(tomoscan_prefix + 'UserName')
    user_pvs['pi_last_name'] = PV(tomoscan_prefix + 'UserLastName')
    user_pvs['pi_affiliation'] = PV(tomoscan_prefix + 'UserInstitution')
    user_pvs['pi_badge'] = PV(tomoscan_prefix + 'UserBadge')
    user_pvs['pi_email'] = PV(tomoscan_prefix + 'UserEmail')
    user_pvs['proposal_number'] = PV(tomoscan_prefix + 'ProposalNumber')
    user_pvs['proposal_title'] = PV(tomoscan_prefix + 'ProposalTitle')
    user_pvs['user_info_update_time'] = PV(tomoscan_prefix + 'UserInfoUpdate')
    user_pvs['experiment_date'] = PV(tomoscan_prefix + 'ExperimentYearMonth')
    return user_pvs

def init(args):
    if not os.path.exists(str(args.config)):
        config.write(str(args.config))
    else:
        raise RuntimeError("{0} already exists".format(args.config))


def show(args):
    """
    Show the currently active proposal info running at beamline
     
    Returns
    -------
    Show experiment information        
    """
    time_now = (datetime.datetime.now() + dt.timedelta(args.set)).astimezone()
    log.info("Today's date: %s" % time_now)
    auth      = authorize.basic(args.credentials)
    run       = scheduling.current_run(auth, args)
    output = scheduling.beamtime_requests(run, auth, args)
    try:
        proposals = output[0]['activities']
        # pprint.pprint(proposals, compact=True)
    except IndexError:
    # if not proposals:
        log.error('No valid current experimentxxx')
        return None
    try:
        log.error(proposals['message'])
        return None
    except:
        pass

    proposal = scheduling.get_current_proposal(proposals, args)
    if proposal != None:
        proposal_pi          = scheduling.get_current_pi(proposal)
        pi_name              = proposal_pi['firstName']
        pi_last_name         = proposal_pi['lastName']   
        pi_affiliation       = proposal_pi['institution']
        pi_email             = proposal_pi['email']
        pi_badge             = proposal_pi['badge']

        proposal_id          = scheduling.get_current_proposal_id(proposal)
        proposal_title       = scheduling.get_current_proposal_title(proposal)
        proposal_user_emails = scheduling.get_current_emails(proposal, False)
        proposal_start_date  = scheduling.get_proposal_starting_date(proposal)
        proposal_start       = dt.datetime.fromisoformat(utils.fix_iso(proposal['startTime']))
        proposal_end         = dt.datetime.fromisoformat(utils.fix_iso(proposal['endTime']))
        log.info("\tRun: %s" % run)
        log.info("\tPI Name: %s %s" % (pi_name, pi_last_name))
        log.info("\tPI affiliation: %s" % (pi_affiliation))
        log.info("\tPI e-mail: %s" % (pi_email))
        log.info("\tPI badge: %s" % (pi_badge))
        log.info("\tProposal GUP: %s" % (proposal_id))
        log.info("\tProposal Title: %s" % (proposal_title))
        log.info("\tStart date: %s" % (proposal_start_date))        
        log.info("\tStart time: %s" % (proposal_start))
        log.info("\tEnd Time: %s" % (proposal_end))
        log.info("\tUser email address: ")
        for ue in proposal_user_emails:
            log.info("\t\t %s" % (ue))
    else:
        time_now = datetime.datetime.now().astimezone() + dt.timedelta(args.set)
        log.warning('No proposal run on %s during %s' % (time_now, run))


def _finish_create(args, exp_name):
    """Shared tail for create and create-manual: confirm, create experiment, add users, print summary."""
    log.info('Create summary:')
    log.info('   Experiment : %s/%s' % (args.year_month, exp_name))
    log.info('   Title      : %s' % args.gup_title)
    if not message.yes_or_no('   *** Confirm? Yes or No'):
        log.info('   Aborted.')
        return

    new_exp = dm.create_experiment(args)
    if new_exp is None:
        return

    dm.add_users(new_exp, args._user_list)

    data_link = dm.make_data_link(args)
    args._final_summary = (exp_name, data_link)


def create(args):
    """
    Create a DM experiment on Sojourner from the APS scheduling system.
    Lists all beamtimes in the current run, lets the operator select one
    interactively, then creates the DM experiment and adds all proposal users.
    """
    auth = authorize.basic(args.credentials)
    if auth is None:
        return
    beamtimes = scheduling.list_beamtimes(auth, args)
    if not beamtimes:
        log.error("No beamtimes found for the current run")
        return
    elif len(beamtimes) == 1:
        bt = beamtimes[0]
        log.info("Found 1 beamtime in run %s: GUP %s (PI: %s, %s)" % (
                  bt['run_name'], bt['gup_number'], bt['pi_last_name'],
                  bt['gup_title'][:60]))
    else:
        log.info("Found %d beamtimes in run %s:" % (
                  len(beamtimes), beamtimes[0]['run_name']))
        for i, bt in enumerate(beamtimes):
            print("  [%2d] GUP %s - PI: %s - %s" % (
                  i, bt['gup_number'], bt['pi_last_name'], bt['gup_title'][:70]))
            print("       %s to %s" % (bt['start_time'], bt['end_time']))
        while True:
            try:
                choice = input("\nSelect beamtime [0-%d] or 'q' to quit: " % (
                               len(beamtimes) - 1)).strip()
                if choice.lower() == 'q':
                    log.info("No beamtime selected. Exiting.")
                    return
                choice = int(choice)
                if 0 <= choice < len(beamtimes):
                    bt = beamtimes[choice]
                    break
                print("Please enter a number between 0 and %d" % (len(beamtimes) - 1))
            except (ValueError, EOFError):
                print("Invalid input. Please enter a number or 'q' to quit.")

    args.year_month     = bt['year_month']
    args.pi_last_name   = bt['pi_last_name']
    args.pi_first_name  = bt['pi_first_name']
    args.pi_institution = bt['pi_institution']
    args.pi_email       = bt['pi_email']
    args.pi_badge       = bt['pi_badge']
    args.gup_number     = bt['gup_number']
    args.gup_title      = bt['gup_title']

    user_list = dm.make_dm_username_list(args)
    exp_name  = dm.make_experiment_name(args)
    if user_list is None:
        log.warning("GUP %s not found in the scheduling system." % args.gup_number)
        log.warning("Experiment '%s' will be created but no users will be added." % exp_name)
        log.info("To add a user afterwards run: dmagic add-user --badge <badge#>")
        user_list = set()
    else:
        log.info('Adding users from the current proposal to the DM experiment.')
    args._user_list = user_list
    _finish_create(args, exp_name)


def create_manual(args):
    """
    Create a DM experiment manually for commissioning runs without a proposal.
    Uses PI metadata and badge numbers supplied on the command line.
    """
    now = datetime.datetime.now()
    if args.date:
        try:
            ref_date = datetime.datetime.strptime(args.date, '%Y-%m')
        except ValueError:
            log.error("Invalid --date '%s': expected format is yyyy-mm (e.g. 2025-12)" % args.date)
            return
    else:
        ref_date = now
    args.year_month     = ref_date.strftime('%Y-%m')
    args.pi_last_name   = args.name
    args.pi_first_name  = args.first_name
    args.pi_institution = args.institution
    args.pi_email       = args.email
    args.pi_badge       = ''
    args.gup_number     = '0'
    args.gup_title      = args.title
    args.manual         = True
    args.manual_start   = ref_date.strftime('%d-%b-%y')
    args.manual_end     = (ref_date + dt.timedelta(days=14)).strftime('%d-%b-%y')
    log.info("Manual experiment: %s-%s, title: %s" % (
              args.year_month, args.pi_last_name, args.gup_title))

    user_list = {'d' + str(args.primary_beamline_contact_badge),
                 'd' + str(args.secondary_beamline_contact_badge)}
    if args.badges:
        for badge in args.badges.split(','):
            badge = badge.strip()
            if badge:
                user_list.add('d' + badge)
    log.info('Adding manual users to the DM experiment.')
    args._user_list = user_list
    _finish_create(args, dm.make_experiment_name(args))


def delete(args):
    """
    Delete a DM experiment from Sojourner.
    Lists all DM experiments for this station (last 2 years) so the operator
    can select one, then deletes it after double confirmation.
    Use --name to bypass the list and delete a known experiment directly.
    """
    if getattr(args, 'exp_name', None):
        # Direct lookup by name (useful for manually created experiments)
        exp_name = args.exp_name
    else:
        exps = dm.list_experiments_by_station(args.experiment_type)
        if not exps:
            log.error('No DM experiments found for station %s (last 2 years).' % args.experiment_type)
            log.error('Use --name EXP_NAME to specify an experiment name directly.')
            return
        log.info('Found %d DM experiment(s) for station %s:' % (len(exps), args.experiment_type))
        for i, e in enumerate(exps):
            start = e.get('startDate', '?')[:10]
            end   = e.get('endDate',   '?')[:10]
            desc  = e.get('description', '')[:60]
            print("  [%2d] %-35s  %s to %s  %s" % (i, e['name'], start, end, desc))
        while True:
            try:
                choice = input("\nSelect experiment to delete [0-%d] or 'q' to quit: " % (
                               len(exps) - 1)).strip()
                if choice.lower() == 'q':
                    log.info('No experiment selected. Exiting.')
                    return
                choice = int(choice)
                if 0 <= choice < len(exps):
                    exp_name = exps[choice]['name']
                    break
                print("Please enter a number between 0 and %d" % (len(exps) - 1))
            except (ValueError, EOFError):
                print("Invalid input. Please enter a number or 'q' to quit.")

    # Fetch full experiment object for storage path details
    exp_obj = dm.get_experiment(exp_name)
    if exp_obj is None:
        log.error('DM experiment not found: %s' % exp_name)
        log.error('Has dmagic create been run for this proposal?')
        return

    log.warning('=' * 60)
    log.warning('*** PERMANENT DELETION — THIS CANNOT BE UNDONE ***')
    log.info('   Experiment     : %s' % exp_name)
    log.info('   Storage dir    : %s' % exp_obj.get('storageDirectory', 'N/A'))
    log.info('   Data dir       : %s' % exp_obj.get('dataDirectory', 'N/A'))
    log.info('   Analysis dir   : %s' % exp_obj.get('analysisDirectory', 'N/A'))
    log.warning('=' * 60)

    if not message.yes_or_no('   *** Are you sure? Yes or No'):
        log.info('   Aborted.')
        return
    if not message.yes_or_no('   *** Confirm AGAIN to permanently delete all data'):
        log.info('   Aborted.')
        return

    dm.delete_experiment(exp_name)


def email(args):
    """
    Send a data-access email with Globus link to all users on a DM experiment.
    Lists all station experiments so the operator can select one.
    """
    exps = dm.list_experiments_by_station(args.experiment_type)
    if not exps:
        log.error('No DM experiments found for station %s.' % args.experiment_type)
        return
    log.info('Found %d DM experiment(s) for station %s:' % (len(exps), args.experiment_type))
    for i, e in enumerate(exps):
        start = e.get('startDate', '?')[:10]
        end   = e.get('endDate',   '?')[:10]
        desc  = e.get('description', '')[:60]
        print("  [%2d] %-35s  %s to %s  %s" % (i, e['name'], start, end, desc))
    while True:
        try:
            choice = input("\nSelect experiment to email [0-%d] or 'q' to quit: " % (
                           len(exps) - 1)).strip()
            if choice.lower() == 'q':
                log.info('No experiment selected. Exiting.')
                return
            choice = int(choice)
            if 0 <= choice < len(exps):
                break
            print("Please enter a number between 0 and %d" % (len(exps) - 1))
        except (ValueError, EOFError):
            print("Invalid input. Please enter a number or 'q' to quit.")

    args._exp_name   = exps[choice]['name']
    args._year_month = exps[choice].get('rootPath', '')

    gup = args._exp_name.rsplit('-', 1)[-1]
    args.presentation_url = tomolog_utils.get_presentation_url(gup, args.tomolog_home)

    log.info('Sending e-mail to users on the DM experiment: %s' % args._exp_name)
    args.msg = message.message(args)
    log.info('   Message preview:')
    log.info('   ' + '=' * 60)
    if args.msg.get_content_maintype() == 'multipart':
        html_content = args.msg.get_payload()[1].get_payload(decode=True).decode()
        for line in message.html_to_text(html_content).splitlines():
            log.info('   %s' % line)
    else:
        for line in args.msg.get_content().splitlines():
            log.info('   %s' % line)
    log.info('   ' + '=' * 60)

    users = dm.list_users_this_dm_exp(args)
    if users:
        emails = dm.make_user_email_list(users)
        for contact in (args.primary_beamline_contact_email,
                        args.secondary_beamline_contact_email):
            if contact not in emails:
                emails.append(contact)
        log.info('   Recipients:')
        for em in emails:
            log.info('      %s' % em)

    message.send_email(args)


def _select_experiment(args, prompt_verb):
    """Show the DM experiment list and return the selected experiment name, or None."""
    exps = dm.list_experiments_by_station(args.experiment_type)
    if not exps:
        log.error('No DM experiments found for station %s.' % args.experiment_type)
        return None
    log.info('Found %d DM experiment(s) for station %s:' % (len(exps), args.experiment_type))
    for i, e in enumerate(exps):
        start = e.get('startDate', '?')[:10]
        end   = e.get('endDate',   '?')[:10]
        desc  = e.get('description', '')[:60]
        print("  [%2d] %-35s  %s to %s  %s" % (i, e['name'], start, end, desc))
    while True:
        try:
            choice = input("\nSelect experiment to %s [0-%d] or 'q' to quit: " % (
                           prompt_verb, len(exps) - 1)).strip()
            if choice.lower() == 'q':
                log.info('No experiment selected. Exiting.')
                return None
            choice = int(choice)
            if 0 <= choice < len(exps):
                return exps[choice]['name']
            print("Please enter a number between 0 and %d" % (len(exps) - 1))
        except (ValueError, EOFError):
            print("Invalid input. Please enter a number or 'q' to quit.")


def remove_user(args):
    """
    Remove one or more users from an existing DM experiment by badge number.
    Lists all station experiments so the operator can select one, then shows
    the current user list before prompting for badge number(s) to remove.
    """
    exp_name = _select_experiment(args, 'remove users from')
    if exp_name is None:
        return

    exp_obj = dm.get_experiment(exp_name)
    if exp_obj is None:
        log.error('DM experiment not found: %s' % exp_name)
        return

    existing = exp_obj.get('experimentUsernameList', [])
    if existing:
        log.info('Current users on %s:' % exp_name)
        for u in sorted(existing):
            log.info('   %s' % u)
    else:
        log.info('No users currently on %s' % exp_name)

    if not args.badges:
        try:
            args.badges = input('Enter badge number(s) to remove (comma-separated): ').strip()
        except EOFError:
            args.badges = ''
    if not args.badges:
        log.error('No badge numbers provided.')
        return

    username_list = set()
    for badge in args.badges.split(','):
        badge = badge.strip()
        if badge:
            username_list.add('d' + badge)

    dm.remove_users(exp_name, username_list)


def add_user(args):
    """
    Add one or more users to an existing DM experiment by badge number.
    Lists all station experiments so the operator can select one.
    """
    exp_name = _select_experiment(args, 'add users to')
    if exp_name is None:
        return

    if not args.badges:
        try:
            args.badges = input('Enter badge number(s) to add (comma-separated): ').strip()
        except EOFError:
            args.badges = ''
    if not args.badges:
        log.error('No badge numbers provided.')
        return

    exp_obj = dm.get_experiment(exp_name)
    if exp_obj is None:
        log.error('DM experiment not found: %s' % exp_name)
        return

    username_list = set()
    for badge in args.badges.split(','):
        badge = badge.strip()
        if badge:
            username_list.add('d' + badge)

    dm.add_users(exp_obj, username_list)


def start_daq(args):
    """
    Select a DM experiment and start automated real-time file transfer (DAQ) to Sojourner.
    The DM system will monitor the analysis machine directory for new files and transfer them.
    """
    exp_name = _select_experiment(args, 'start DAQ for')
    if exp_name is None:
        return
    dm.start_daq(exp_name, args.analysis, args.analysis_top_dir)


def stop_daq(args):
    """
    Select a DM experiment and stop all running DAQs for it.
    """
    exp_name = _select_experiment(args, 'stop DAQ for')
    if exp_name is None:
        return
    dm.stop_daq(exp_name)


def _update_tag_pvs(args, pi, proposal_num, proposal_title, exp_date):
    """Initialize EPICS PVs, verify connectivity, and write user/experiment fields.

    Parameters
    ----------
    args         : CLI args (needs tomoscan_prefix, epics_conn_timeout)
    pi           : dict with keys firstName, lastName, institution, email, badge
    proposal_num : str — GUP number or manual identifier
    proposal_title : str
    exp_date     : str — 'YYYY-MM'

    Returns True on success, False if the IOC is unreachable.
    """
    user_pvs     = init_PVs(args)
    probe_keys   = ('user_info_update_time', 'pi_name')
    conn_timeout = getattr(args, 'epics_conn_timeout', 1.0)

    missing = []
    for k in probe_keys:
        pv = user_pvs.get(k)
        if pv is None:
            continue
        if not pv.wait_for_connection(timeout=conn_timeout):
            missing.append(pv.pvname)

    if missing:
        log.error("EPICS IOC %s not reachable" % args.tomoscan_prefix)
        log.error("Verify tomoscan_prefix=%s is running" % args.tomoscan_prefix)
        log.error("or select a different IOC by using the --tomoscan-prefix option")
        return False

    log.info("User/Experiment PV update")
    user_pvs['pi_name'].put(pi['firstName'])
    log.info('Updating pi_name EPICS PV with: %s' % pi['firstName'])
    user_pvs['pi_last_name'].put(pi['lastName'])
    log.info('Updating pi_last_name EPICS PV with: %s' % pi['lastName'])
    user_pvs['pi_affiliation'].put(pi['institution'])
    log.info('Updating pi_affiliation EPICS PV with: %s' % pi['institution'])
    user_pvs['pi_email'].put(pi['email'])
    log.info('Updating pi_email EPICS PV with: %s' % pi['email'])
    user_pvs['pi_badge'].put(pi['badge'])
    log.info('Updating pi_badge EPICS PV with: %s' % pi['badge'])

    us_central_tz  = zoneinfo.ZoneInfo("America/Chicago")
    local_time_iso = datetime.datetime.now().replace(tzinfo=us_central_tz).isoformat()
    user_pvs['user_info_update_time'].put(local_time_iso)
    log.info('Updating user_info_update_time EPICS PV with: %s' % local_time_iso)

    user_pvs['proposal_number'].put(proposal_num)
    log.info('Updating proposal_number EPICS PV with: %s' % proposal_num)
    user_pvs['proposal_title'].put(proposal_title)
    log.info('Updating proposal_title EPICS PV with: %s' % proposal_title)
    user_pvs['experiment_date'].put(exp_date)
    log.info('Updating experiment_date EPICS PV with: %s' % exp_date)
    return True


def tag(args):
    """
    Update the EPICS PVs with user and experiment information associated with the current experiment

    Parameters
    ----------
    args : parameters passed at the CLI, see config.py for full options
    """
    now = datetime.datetime.today()
    log.info("Today's date: %s" % now)

    auth   = authorize.basic(args.credentials)
    run    = scheduling.current_run(auth, args)
    output = scheduling.beamtime_requests(run, auth, args)

    proposals = None
    try:
        proposals = output[0]['activities']
    except (IndexError, TypeError):
        pass

    if not proposals:
        log.error('No proposal found in the scheduling system for this run')
        log.error("Create one with 'dmagic create' (or 'dmagic create-manual' for commissioning)")
        log.error("then run 'dmagic tag-manual' to pick it and update the EPICS PVs")
        return None
    try:
        log.error(proposals['message'])
        return None
    except Exception:
        pass

    proposal = scheduling.get_current_proposal(proposals, args)
    if proposal is None:
        time_now = datetime.datetime.now().astimezone() + dt.timedelta(args.set)
        log.warning('No proposal active on %s during run %s' % (time_now, run))
        log.warning("Use 'dmagic tag-manual' to select an experiment manually")
        return None

    pi             = scheduling.get_current_pi(proposal)
    proposal_num   = str(scheduling.get_current_proposal_id(proposal))
    proposal_title = str(scheduling.get_current_proposal_title(proposal))
    start_datetime = datetime.datetime.strptime(utils.fix_iso(proposal['startTime']), '%Y-%m-%dT%H:%M:%S%z')
    exp_date       = start_datetime.strftime('%Y-%m')

    _update_tag_pvs(args, pi, proposal_num, proposal_title, exp_date)


def tag_manual(args):
    """
    Interactively select a DM experiment and update EPICS PVs with its information.

    Lists all DM experiments for the station (scheduling-based and manually created)
    sorted newest first, then lets the operator choose which one to activate.
    Useful when sneaking in a sample from a different user group, or when running
    commissioning with no proposal in the scheduling system.

    Parameters
    ----------
    args : parameters passed at the CLI, see config.py for full options
    """
    now = datetime.datetime.today()
    log.info("Today's date: %s" % now)

    exps = dm.list_experiments_by_station(args.experiment_type)
    if not exps:
        log.error('No DM experiments found for station %s' % args.experiment_type)
        return

    log.info('Found %d DM experiment(s) for station %s:' % (len(exps), args.experiment_type))
    for i, e in enumerate(exps):
        start = e.get('startDate', '?')[:10]
        end   = e.get('endDate',   '?')[:10]
        desc  = e.get('description', '')[:60]
        print("  [%2d] %-35s  %s to %s  %s" % (i, e['name'], start, end, desc))

    while True:
        try:
            choice = input("\nSelect experiment to tag [0-%d] or 'q' to quit: " % (
                           len(exps) - 1)).strip()
            if choice.lower() == 'q':
                log.info('No experiment selected. Exiting.')
                return
            choice = int(choice)
            if 0 <= choice < len(exps):
                break
            print("Please enter a number between 0 and %d" % (len(exps) - 1))
        except (ValueError, EOFError):
            print("Invalid input. Please enter a number or 'q' to quit.")

    exp = exps[choice]
    log.info('Selected DM experiment: %s' % exp['name'])

    # Experiment name format: YYYY-MM-LastName-GUP
    name_parts     = exp['name'].split('-')
    pi_last        = name_parts[2] if len(name_parts) >= 4 else ''
    gup_str        = name_parts[-1] if len(name_parts) >= 4 else '0'
    proposal_title = exp.get('description', exp['name'])
    exp_date       = exp.get('rootPath', '')

    # For non-zero GUP numbers try to pull full PI info from the scheduling system
    pi = None
    if gup_str.isdigit() and int(gup_str) != 0:
        try:
            auth     = authorize.basic(args.credentials)
            beamtime = scheduling.get_beamtime(gup_str, auth, args)
            if beamtime is not None:
                pi = scheduling.get_current_pi(beamtime)
                log.info('Retrieved full PI info from scheduling system for GUP %s' % gup_str)
        except Exception as e:
            log.warning('Could not retrieve PI info from scheduling system: %s' % str(e))

    if pi is None:
        log.warning('Using PI info parsed from DM experiment name (first name, institution, email, badge will be empty)')
        pi = {'firstName': '', 'lastName': pi_last, 'institution': '', 'email': '', 'badge': ''}

    _update_tag_pvs(args, pi, gup_str, proposal_title, exp_date)


def main():
    home = os.path.expanduser("~")
    logs_home = home + '/logs/'

    # make sure logs directory exists
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)

    lfname = logs_home + 'dmagic_' + datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
    log.setup_custom_logger(lfname)

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', **config.SECTIONS['general']['config'])

    # (sections shown in -h, sections suppressed in -h but still parsed, help text)
    cmd_parsers = [
        ('init',          init,          config.INIT_PARAMS,   (),                   "Create configuration file"),
        ('show',          show,          config.SHOW_PARAMS,   config.SITE_SUPPRESS, "Show user and experiment info from the APS schedule"),
        ('tag',           tag,           config.TAG_PARAMS,    config.SITE_SUPPRESS, "Update user info EPICS PVs with info from the APS schedule"),
        ('tag-manual',    tag_manual,    config.TAG_PARAMS,    config.SITE_SUPPRESS, "Interactively pick a DM experiment and update user info EPICS PVs"),
        ('create',        create,        config.CREATE_PARAMS, config.SITE_SUPPRESS, "Create a DM experiment from the APS scheduling system"),
        ('create-manual', create_manual, config.MANUAL_PARAMS, config.SITE_SUPPRESS, "Create a DM experiment manually for commissioning runs"),
        ('delete',        delete,        config.CREATE_PARAMS, config.SITE_SUPPRESS, "Delete a DM experiment from Sojourner"),
        ('email',         email,         config.EMAIL_PARAMS,  config.SITE_SUPPRESS, "Send data-access email with Globus link to all users on the DM experiment"),
        ('daq-start',     start_daq,     config.DAQ_PARAMS,    config.SITE_SUPPRESS, "Start automated real-time file transfer (DAQ) to Sojourner"),
        ('daq-stop',      stop_daq,      config.DAQ_PARAMS,    config.SITE_SUPPRESS, "Stop all running file transfers for the current experiment"),
        ('add-user',      add_user,      config.CREATE_PARAMS, config.SITE_SUPPRESS, "Add users to an existing DM experiment by badge number"),
        ('remove-user',   remove_user,   config.CREATE_PARAMS, config.SITE_SUPPRESS, "Remove users from an existing DM experiment by badge number"),
    ]

    subparsers = parser.add_subparsers(title="Commands", metavar='')

    for cmd, func, sections, suppress, text in cmd_parsers:
        cmd_params = config.Params(sections=sections, suppress_sections=suppress)
        cmd_parser = subparsers.add_parser(cmd, help=text, description=text, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        cmd_parser = cmd_params.add_arguments(cmd_parser)
        if cmd == 'delete':
            cmd_parser.add_argument(
                '--exp-name', default=None, type=str, metavar='EXP_NAME',
                help='[Optional] Full DM experiment name, used only to delete commissioning '
                     'experiments created with "dmagic create-manual" that are not in the '
                     'APS scheduling system (e.g. 2026-03-Staff-0). Leave blank to select '
                     'from the list of all station experiments.')
        if cmd in ('add-user', 'remove-user'):
            cmd_parser.add_argument(
                '--badges', default='', type=str, metavar='BADGES',
                help='Comma-separated badge number(s) to add/remove (e.g. 12345 or 12345,67890)')
        cmd_parser.set_defaults(_func=func)

    args = config.parse_known_args(parser, subparser=True)

    if not hasattr(args, '_func'):
        parser.print_help()
        sys.exit(0)

    try:
        args._func(args)
        config.log_values(args)
        if hasattr(args, '_final_summary'):
            exp_name, data_link = args._final_summary
            sep = '=' * 60
            log.info(sep)
            log.info('Experiment name : %s' % exp_name)
            log.info('Globus data link: %s' % data_link)
            log.info(sep)
        # Write sections appropriate to each command.
        # Always include 'site' so beamline-specific settings are preserved
        # rather than being reset to code defaults.
        cmd = sys.argv[1] if len(sys.argv) > 1 else ''
        if cmd == 'init':
            write_sections = ('site',)
        elif cmd == 'create-manual':
            write_sections = ('manual', 'settings', 'site')
        elif cmd in ('daq-start', 'daq-stop'):
            write_sections = ('local', 'settings', 'site')
        else:
            write_sections = ('settings', 'site')
        config.write(args.config, args=args, sections=write_sections)
    except RuntimeError as e:
        log.error(str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
