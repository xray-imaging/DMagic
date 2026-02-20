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


def tag(args):
    """
    Update the EPICS PVs with user and experiment information associated with the current experiment

    Parameters
    ----------
    args : parameters passed at the CLI, see config.py for full options
    """
    # set the experiment date 
    now = datetime.datetime.today()
    log.info("Today's date: %s" % now)

    auth      = authorize.basic(args.credentials)
    run       = scheduling.current_run(auth, args)
    output = scheduling.beamtime_requests(run, auth, args)
    proposals = output[0]['activities']
    # pprint.pprint(proposals, compact=True)
    #proposals = scheduling.beamtime_requests(run, auth, args)

    if not proposals:
        log.error('No valid current experiment')
        return None
    try:
        log.error(proposals['message'])
        return None
    except:
        pass

    proposal = scheduling.get_current_proposal(proposals, args)

    if proposal != None:
        # get PI information
        pi = scheduling.get_current_pi(proposal)

        user_pvs = init_PVs(args)

        # Verify IOC/PVs are reachable before attempting any puts
        probe_keys = ('user_info_update_time', 'pi_name')  # pick PVs that always exist
        conn_timeout = getattr(args, 'epics_conn_timeout', 1.0)  # optional new arg; fallback 1s

        missing = []
        for k in probe_keys:
            pv = user_pvs.get(k)
            if pv is None:
                continue
            if not pv.wait_for_connection(timeout=conn_timeout):
                missing.append(pv.pvname)

        if missing:
            log.error("EPICS IOC %s not reachable" % (args.tomoscan_prefix))
            log.error("Verify tomoscan_prefix=%s is running " % (args.tomoscan_prefix))
            log.error("or select select a different IOC by using the --tomoscan-prefix option")
            return None


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

        # set iso format time
        us_central_tz = zoneinfo.ZoneInfo("America/Chicago")
        local_time_iso = datetime.datetime.now().replace(tzinfo=us_central_tz).isoformat()
        user_pvs['user_info_update_time'].put(local_time_iso)
        log.info('Updating user_info_update_time EPICS PV with: %s' % local_time_iso)
        
        # get experiment information
        user_pvs['proposal_number'].put(str(scheduling.get_current_proposal_id(proposal)))
        log.info('Updating proposal_number EPICS PV with: %s' % scheduling.get_current_proposal_id(proposal))
        user_pvs['proposal_title'].put(str(scheduling.get_current_proposal_title(proposal)))
        log.info('Updating proposal_title EPICS PV with: %s' % scheduling.get_current_proposal_title(proposal))
        #Make the start date of the experiment into a year - month
        start_datetime = datetime.datetime.strptime(utils.fix_iso(proposal['startTime']),'%Y-%m-%dT%H:%M:%S%z')
        user_pvs['experiment_date'].put(start_datetime.strftime('%Y-%m'))
        log.info('Updating experiment_date EPICS PV with: %s' % start_datetime.strftime('%Y-%m'))
    else:
        time_now = datetime.datetime.now().astimezone() + dt.timedelta(args.set)
        log.warning('No proposal run on %s during %s' % (time_now, run))


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
    show_params = config.DMAGIC_PARAMS
    tag_params = config.DMAGIC_PARAMS

    cmd_parsers = [
        ('init',        init,           (),                             "Create configuration file"),
        ('show',        show,           show_params,                    "Show user and experiment info from the APS schedule"),
        ('tag',         tag,            tag_params,                     "Update user info EPICS PVs with info from the APS schedule"),
    ]

    subparsers = parser.add_subparsers(title="Commands", metavar='')

    for cmd, func, sections, text in cmd_parsers:
        cmd_params = config.Params(sections=sections)
        cmd_parser = subparsers.add_parser(cmd, help=text, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        cmd_parser = cmd_params.add_arguments(cmd_parser)
        cmd_parser.set_defaults(_func=func)

    args = config.parse_known_args(parser, subparser=True)

    try:
        # load args from default (config.py) if not changed
        args._func(args)
        config.log_values(args)
        # undate globus.config file
        sections = config.DMAGIC_PARAMS
        config.write(args.config, args=args, sections=sections)
    except RuntimeError as e:
        log.error(str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
