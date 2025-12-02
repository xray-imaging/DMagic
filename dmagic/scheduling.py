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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #f
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
Module containing routines to access the APS scheduling system.

You must create in your home directory a 
`scheduling.ini <https://github.com/decarlof/data-management/blob/master/config/scheduling.ini>`__ 
configuration file

"""

import os
import json
import sys
import pytz 
import requests

import datetime as dt

from os.path import expanduser

from dmagic import log
from dmagic import utils


__author__ = "Francesco De Carlo"
__credits__ = "John Hammonds"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['current_run',
           'beamtime_requests',
           'get_current_users',
           'get_current_pi',
           'get_current_proposal_id',
           'get_current_proposal_title',
           'get_current_proposal',
           'get_current_emails',
           ]

debug = False


def current_run(auth, args):
    """
    Determine the current run

    Parameters
    ----------
    auth : Basic http authorization object
        Basic http authorization.


    Returns
    -------
    run : string
        Run name 2024-1.
    """
    end_point         = "beamline-scheduling/sched-api/run/getAllRuns"
    api_url = args.url + "/" + end_point 

    reply = requests.get(api_url, auth=auth)

    if reply.status_code == 200:
        start_times = [item['startTime'] for item in reply.json()]
        end_times   = [item['endTime']   for item in reply.json()]
        runs        = [item['runName']   for item in reply.json()]
        
        time_now = dt.datetime.now(pytz.timezone('America/Chicago')) + dt.timedelta(args.set)
        for i in range(len(start_times)):
            prop_start = dt.datetime.fromisoformat(utils.fix_iso(start_times[i]))
            prop_end   = dt.datetime.fromisoformat(utils.fix_iso(end_times[i]))
            if prop_start <= time_now and prop_end >= time_now:
                return runs[i]
    else:
        log.error("No response from the restAPI. Error: %s" % reply.status_code)    
    return None


def beamtime_requests(run, auth, args):
    """
    Get a dictionary-like object with all proposals that have a beamtime request scheduled during the run.
    If no proposal is active or auth does not have permission for beamline, return None.
    
    Parameters
    ----------
    run : string
        Run name e.g. '2024-1'
    auth : Basic http authorization object
        Basic http authorization.
    beamline : string
        beamline ID as stored in the APS scheduling system, e.g. 2-BM-A,B or 7-BM-B or 32-ID-B,C

    Returns
    -------
    proposals : list
        dict-like object with proposals that have a beamtime request scheduled during the run.
        Returns None if there are no proposals or if auth does not have permission for beamline.
    """
    if not run:
        return None
    else:
        #end_point="beamline-scheduling/sched-api/activity/findByRunNameAndBeamlineId"
        end_point="beamline-scheduling/sched-api/schedule/findByRunNameAndScheduleName"
        api_url = args.url + "/" + end_point + "/" + run + "/" + args.beamline
        reply = requests.get(api_url, auth=auth)

        return reply.json()


def get_current_users(proposal):
    """
    Get users listed in the currently active proposal.
     
    Parameters
    ----------
    proposal : dictionary-like object containing proposal information
    
    Returns
    -------
    users : dictionary-like object containing user information      
    """
    if not proposal:
        print("No current valid proposal")
        return None
    return proposal['beamtime']['proposal']['experimenters']


def get_current_pi(proposal):
    """
    Get information about the currently active proposal PI.
     
    Parameters
    ----------
    proposal : dictionary-like object containing proposal information
    
    Returns
    -------
    dictionary-like object containing PI information
    """
    users = get_current_users(proposal)
    for u in users:
        if 'piFlag' in u.keys():
            if u['piFlag'] == 'Y':
                return u
    # If we are here, nothing was listed as PI.  Use first user
    return users[0]


def get_current_proposal_id(proposal):
    """
    Get the proposal id for the currently active proposal.
     
    Parameters
    ----------
    proposal : dictionary-like object containing proposal information

    Returns
    -------
    currently active proposal ID as an int
    """
    if not proposal:
        print("No current valid proposal")
        return None
    return proposal['beamtime']['proposal']['gupId']


def get_current_proposal_title(proposal):
    """
    Get the title of the currently active proposal.
     
    Parameters
    ----------
    proposal : dictionary-like object containing proposal information
    
    Returns
    -------
    str: title of the currently active proposal
    """
    if not proposal:
        print("No current valid proposal")
        return None
    return proposal['beamtime']['proposal']['proposalTitle']
     

def get_current_proposal(proposals, args):
    """
    Get a dictionary-like object with currently active proposal information.
    If no proposal is active, return None
     
    Parameters
    ----------
    proposal : dictionary-like object containing proposal information
    
    Returns
    -------
    dict-like object with information for currently active proposal
    """
    time_now = dt.datetime.now(pytz.timezone('America/Chicago')) + dt.timedelta(args.set)
    for prop in proposals:
        prop_start = dt.datetime.fromisoformat(utils.fix_iso(prop['startTime']))
        prop_end = dt.datetime.fromisoformat(utils.fix_iso(prop['endTime']))
        if prop_start <= time_now and prop_end >= time_now:
            # pprint.pprint(prop, compact=True)
            return prop
    return None


def get_current_emails(proposal, exclude_pi=True):
    """
    Find user's emails listed in the currently active proposal
     
    Parameters
    ----------
    proposal : dictionary-like object containing proposal information
    
    Returns
    -------
    List of user emails (default: all but PI)       
    """
    emails = []
    
    users = get_current_users(proposal)

    if not users:
        return None

    for u in users:
        if exclude_pi and 'piFlag' in u.keys() and u['piFlag'] == 'Y':
            continue
        if 'email' in u.keys() and u['email'] != None:
            emails.append(str(u['email']).lower())
            # print('Added {0:s} to the e-mail list.'.format(emails[-1]))
        else:            
            print("    Missing e-mail for badge {0:6d}, {1:s} {2:s}, institution {3:s}"
                    .format(u['badge'], u['firstName'], u['lastName'], u['institution']))
    return emails

def get_proposal_starting_date(proposal):
    """
    Get the proposal starting date for the current proposal.

    Returns
    ---------
    proposal starting date as a string
    """
    if not proposal:
        log.error("No current valid proposal")
        return None
    log.info("Found valid proposal start time")
    return str(dt.datetime.fromisoformat((proposal['startTime'])).strftime("%Y_%m_%d"))
