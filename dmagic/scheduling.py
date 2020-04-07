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
from os.path import expanduser
import datetime
from suds.wsse import Security, UsernameToken
from suds.client import Client
from suds.transport.https import HttpAuthenticated
import logging
import sys
import traceback
import urllib.request
import http.client
from xml.sax import SAXParseException
import ipdb
from collections import defaultdict
import configparser
import unicodedata
import string

from dmagic import log


__author__ = "Francesco De Carlo"
__credits__ = "John Hammonds"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['get_users',
           'find_emails',
           'find_pi_info',
           'find_experiment_info',
           ]

debug = False

class HTTPSConnectionV3(http.client.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        http.client.HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        try:
            print ("using connection")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, \
                                        ssl_version=ssl.PROTOCOL_SSLv3)
        except ssl.SSLError as e:
            log.error("Trying SSLv3.")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, \
                                        ssl_version=ssl.PROTOCOL_SSLv23)

class HTTPSHandlerV3(urllib.request.HTTPSHandler):
    def https_open(self, req):
        log.info("using this opener")
        return self.do_open(HTTPSConnectionV3, req)

def setSoapHeader(client, username, password):
    security = Security()
    token = UsernameToken(username, password)
    token.setcreated()
    security.tokens.append(token)
    if debug:
        log.warning(security)
    client.set_options(wsse=security)

def findRunName(args, startDate, endDate):
    """Find the official run name for the run that spans the
    given startDate and endDate

    Returns string."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    try:
        result = runScheduleServiceClient.service.findAllRuns()
    except Exception:
        log.error("Exception ERROR in findRunName")
        log.error("Unable to contact data servicesl")
        log.error("Request timed out.")
        log.error("The request timeout for the sent message was reached without receiving a response from the server.")
        sys.exit(2)
    except soapFault:
        log.error("Soap fault ERROR in findRunName")
        log.error(soapFault)
        sys.exit(2)
    runArray = result.run
    runName = None
    for run in runArray:

        try:
            start_time = run.startTime.replace(tzinfo=None)
            end_time = run.endTime.replace(tzinfo=None)
            if startDate >= start_time and endDate <= end_time:
                runName = run.runName
                break
        except Exception as ex:
            log.error("ERROR caught in findRunName:" + str(ex))
            log.error(startDate)
            log.error(run.startTime)
            log.error(endDate)
            log.error(run.endTime)
            raise ex
    return runName

def findBeamlineSchedule(args, beamlineName, runName):
    """Find beamline schedule for given beamlineName and runName"""

    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    try:
        result  = beamlineScheduleServiceClient.service.findBeamlineSchedule(beamlineName, runName)
    except SAXParseException as ex:
        log.info("ERROR in findBeamlineSchedule\n")
        traceback.print_exc()
        sys.exit(2)

    return result

def findBeamtimeRequestsByBeamline(beamlineName, runName):
    """Find beamline schedule for given beamlineName and runName

    Returns schedule object."""
    try:
        result  = beamlineScheduleServiceClient.service.findBeamtimeRequestsByBeamline(beamlineName, runName)
    except SAXParseException:
        log.info("ERROR in findBeamtimeRequestsByBeamline")
    except Exception:
        log.info("ERROR in findBeamtimeRequestByBeamline\n")
        traceback.print_exc()
        sys.exit(2)
    return result

def setup_connection(args):
    
    # home = expanduser("~")
    # credentials = os.path.join(home, 'scheduling.ini')
    
    # cf = configparser.ConfigParser()
    # cf.read(credentials)
    username = args.username
    password = args.password
    beamline = args.beamline
    
    # Uncomment one if using ANL INTERNAL or EXTERNAL network
    #base = cf.get('hosts', 'internal')
    # base = args.internal
    base = args.external

    result = urllib.request.install_opener(urllib.request.build_opener(HTTPSHandlerV3()))
    logging.raiseExceptions = 0

    beamlineScheduleServiceURL = base + \
         'beamlineScheduleService/beamlineScheduleWebService.wsdl'

    runScheduleServiceURL = base + \
         'runScheduleService/runScheduleWebService.wsdl'

    try:
        credentials = dict(username=username, password=password)
        t = HttpAuthenticated(**credentials)
        if debug:
            print(t.u2handlers())
            print(t.credentials())
        runScheduleServiceClient = Client(runScheduleServiceURL)
        runScheduleServiceClient.options.cache.setduration(seconds=10)
        result = setSoapHeader(runScheduleServiceClient, username, password)
        beamlineScheduleServiceClient = Client(beamlineScheduleServiceURL)
        beamlineScheduleServiceClient.options.cache.setduration(seconds=10)
        result = setSoapHeader(beamlineScheduleServiceClient, username, password)
    except Exception as ex:
        log.error("CANNOT OPEN SERVICES:" + str(ex))
        # raise
        exit(-1)

    return runScheduleServiceClient, beamlineScheduleServiceClient, beamline

def get_users(args, date=None):
    """
    Get users running at beamline at a specific date
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    users : dictionary-like object containing user information      
    """
    
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(args, date, date)
    schedule = findBeamlineSchedule(args, beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            start_time = event.startTime.replace(tzinfo=None)
            ed = event.endTime.replace(tzinfo=None)
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= start_time and date <= ed:
                        for experimenter in event.beamtimeRequest.proposal.experimenters.experimenter:
                            for key in experimenter.__keylist__:
                                users[experimenter.lastName][key] = getattr(experimenter, key)
        except:
            ipdb.set_trace()
            raise

    return users

def get_proposal_id(args, date=None):
    """Find the proposal number (GUP) for a given beamline and date

    Returns proposal id."""

    proposal_id = "empty_proposal_id"
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(args, date, date)
    schedule = findBeamlineSchedule(args, beamline, run_name)

    events = schedule.activities.activity

    users = defaultdict(dict)
    for event in events:
        try:
            start_time = event.startTime.replace(tzinfo=None)
            ed = event.endTime.replace(tzinfo=None)

            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= start_time and date <= ed:
                        proposal_id = str(event.beamtimeRequest.proposal.id)
        except:
            ipdb.set_trace()
            raise

    return proposal_id


def get_proposal_title(args, date=None):
    """Find the proposal title for a given beamline and date

    Returns proposal title."""

    proposal_title = "empty_proposal_title"
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(args, date, date)
    schedule = findBeamlineSchedule(args, beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            start_time = event.startTime.replace(tzinfo=None)
            ed = event.endTime.replace(tzinfo=None)
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= start_time and date <= ed:
                        proposal_title = event.beamtimeRequest.proposal.proposalTitle
        except:
            ipdb.set_trace()
            raise
    return clean_entry(proposal_title)


def get_experiment_start(args, date=None):
    """Find the experiment start date for a given beamline and date

    Returns experiment_start."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(args, date, date)
    schedule = findBeamlineSchedule(args, beamline, run_name)
    experiment_start = date

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            start_time = event.startTime.replace(tzinfo=None)
            ed = event.endTime.replace(tzinfo=None)

            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= start_time and date <= ed:
                        experiment_start = event.startTime
        except:
            ipdb.set_trace()
            raise

    return experiment_start


def get_experiment_end(args, date=None):
    """Find the experiment end date for a given beamline and date

    Returns experiment_end."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(args, date, date)
    schedule = findBeamlineSchedule(args, beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            start_time = event.startTime.replace(tzinfo=None)
            ed = event.endTime.replace(tzinfo=None)

            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= start_time and date <= ed:
                        experiment_end = event.endTime
        except:
            ipdb.set_trace()
            raise

    return experiment_end


def get_beamtime_request(args, date=None):
    """Find the proposal beamtime request id for a given beamline and date

    Returns users."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(args, date, date)
    schedule = findBeamlineSchedule(args, beamline, run_name)

    events = schedule.activities.activity

    users = defaultdict(dict)
    for event in events:
        try:
            start_time = event.startTime.replace(tzinfo=None)
            ed = event.endTime.replace(tzinfo=None)

            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= start_time and date <= ed:
                        beamtime_requestart_time = event.beamtimeRequest.id
        except:
            ipdb.set_trace()
            raise

    return beamtime_request


def find_pi_info(args, date=None):
    """
    Find info the Principal Investigator (PI) running at beamline at a specific date
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    last_name : str
        PI last name as a valid folder name       
    """

    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)

    users = get_users(args, date)

    pi = dict()

    pi['name'] = "empty pi_full_name"
    pi['last_name'] = "empty pi_last_name"
    pi['institution'] = "empty pi_institution"
    pi['badge'] =  "empty pi_badge" 
    pi['email'] = "empty pi_email"

    for tag in users:
        if users[tag].get('piFlag') != None:
            pi['name'] = str(strip_accents(users[tag]['firstName']) + ' ' + strip_accents(users[tag]['lastName']))
            pi['last_name'] = strip_accents(users[tag]['lastName'])      
            pi['institution'] = str(strip_accents(users[tag]['institution']))
            pi['institution'] = pi['institution'][:256]
            pi['badge'] = str(users[tag]['badge'])
            pi['email'] = str(users[tag]['email'])
    
    return pi


def find_experiment_info(args, date=None):
    """
    Find experiment info (GUP, Title, Start date)
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    experiment id       
    """
       
    datetime_format = '%Y-%m'

    experiment = dict()
   
    # scheduling system settings
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    experiment['id'] = get_proposal_id(args, date.replace(tzinfo=None))
    experiment['title'] = get_proposal_title(args, date.replace(tzinfo=None))
    experiment['title'] = experiment['title'][:256]
    experiment['start'] = get_experiment_start(args, date.replace(tzinfo=None))
    experiment['start'] = str(experiment['start'].strftime(datetime_format))

    return experiment


def find_experiment_start(args, date=None):
    """
    Find the experiment starting date
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    Experiment Stating date : date        
    """

    # scheduling system settings
    log.info("Finding experiment start date ... ")
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)

    experiment_start = get_experiment_start(args, date.replace(tzinfo=None))
 
    return experiment_start


def find_users(args, date=None):
    """
    Find users running at beamline at a specific date
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    users : dictionary-like object containing user information        
    """

    log.info("Finding users ... ")
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    users = get_users(args, date.replace(tzinfo=None))
    
    return users


def find_pi_last_name(args, date=None):
    """
    Find the Principal Investigator (PI) running at beamline at a specific date
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    last_name : str
        PI last name as a valid folder name       
    """
    log.info("Finding PI last name ... ")
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)
    users = get_users(args, date.replace(tzinfo=None))

    for tag in users:
        if users[tag].get('piFlag') != None:
            first_name = str(users[tag]['firstName']) 
            last_name = str(users[tag]['lastName'])            
            role = "*"
            institution = str(strip_accents(users[tag]['institution']))
            badge = str(users[tag]['badge'])
            email = str(users[tag]['email'])

    return clean_entry(last_name)     


def print_users(users):
    """
    Print the users running at beamline at a specific date
     
    Parameters
    ----------
    users : dictionary-like object containing user information
    
    
    Returns
    -------
    Print user info        
    """
    for tag in users:
        if users[tag].get('piFlag') != None:
            role = "*"
        else:            
            role = " "

        log.info("[%s, %s %s, %s, %s] %s" % (users[tag]['badge'], users[tag]['firstName'], users[tag]['lastName'], strip_accents(users[tag]['institution']), users[tag]['email'], role))

    log.info("[*] Proposal PI")


def find_emails(users, exclude_pi=True):
    """
    Find user's emails running at beamline at a specific date)
     
    Parameters
    ----------
    users : dictionary-like object containing user information
    
    
    Returns
    -------
    List of user emails (default: all but PI)       
    """
    emails = []
    i = 0

    for lastname in users:
        if exclude_pi:
            if users[lastname].get('piFlag') == None:
                if users[lastname].get('email') != None:
                    email = str(users[lastname]['email'])
                    emails.append(email.lower())
                else:            
                    log.info("\tMissing e-mail for:", users[lastname]['badge'], users[lastname]['firstName'], users[lastname]['lastName'], strip_accents(users[lastname]['institution']))
        else:
            if users[lastname].get('email') != None:
                email = str(users[lastname]['email'])
                emails.append(email.lower())
            else:            
                log.info("\tMissing e-mail for:", users[lastname]['badge'], users[lastname]['firstName'], users[lastname]['lastName'], strip_accents(users[lastname]['institution']))
    return emails


def print_experiment_info(args, date=None):
    """
    Print the experiment info running at beamline at a specific date
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    Print experiment information        
    """
    log.info("Inputs: ")
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
    log.info("\tTime of Day: ", date.strftime(datetime_format))
    log.info("\tBeamline: ", beamline)

    # scheduling system settings
    log.info("\tAccessing the APS Scheduling System ... ")
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection(args)

    run_name = findRunName(args, now.replace(tzinfo=None), now.replace(tzinfo=None))
    proposal_title = get_proposal_title(args, date.replace(tzinfo=None))
    users = get_users(args, beamline, date.replace(tzinfo=None))
    experiment_start = get_experiment_start(args, date.replace(tzinfo=None))
    experiment_end = get_experiment_end(args, date.replace(tzinfo=None))

    log.info("\tRun Name: ", run_name) 
    log.info("\tProposal Title: ", proposal_title)
    log.info("\tExperiment Start: ", experiment_start)
    log.info("\tExperiment End: ", experiment_end)
    # print user emails
    log.info("\tUser email address: ")
    for tag in users:
        if users[tag].get('email') != None:
            email = str(users[tag]['email'])
            log.info("\t\t", email)
        else:            
            log.info("\tMissing e-mail for:", users[tag]['badge'], users[tag]['firstName'], users[tag]['lastName'], strip_accents(users[tag]['institution']))


def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
                  
def clean_entry(entry):
    """
    Remove from user last name characters that are not compatible folder names.
     
    Parameters
    ----------
    entry : str
        user last name    
    Returns
    -------
    entry : str
        user last name compatible with directory name   
    """

    valid_folder_entry_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    utf_8_str = str(entry) 
    norml_str = unicodedata.normalize('NFKD', utf_8_str)
    cleaned_folder_name = norml_str.encode('ASCII', 'ignore')
    
    cfn = norml_str.replace(' ', '_')  
    return ''.join(c for c in list(cfn) if c in list(valid_folder_entry_chars))
