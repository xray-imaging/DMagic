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
import urllib2
import httplib
from xml.sax import SAXParseException
import ipdb
from collections import defaultdict
import ConfigParser
import unicodedata
import string
__author__ = "Francesco De Carlo"
__credits__ = "John Hammonds"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['create_experiment_id',
           'find_experiment_start',
           'find_pi_last_name',
           'find_users',
           'find_pi_info',
           'find_experiment_info',
           'print_experiment_info',
           'print_users'
           ]

debug = False

class HTTPSConnectionV3(httplib.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        try:
            print ("using connection")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, \
                                        ssl_version=ssl.PROTOCOL_SSLv3)
        except ssl.SSLError, e:
            print("Trying SSLv3.")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, \
                                        ssl_version=ssl.PROTOCOL_SSLv23)

class HTTPSHandlerV3(urllib2.HTTPSHandler):
    def https_open(self, req):
        print "using this opener"
        return self.do_open(HTTPSConnectionV3, req)

def setSoapHeader(client, username, password):
    security = Security()
    token = UsernameToken(username, password)
    token.setcreated()
    security.tokens.append(token)
    if debug:
        print security
    client.set_options(wsse=security)

def findRunName(startDate, endDate):
    """Find the official run name for the run that spans the
    given startDate and endDate

    Returns string."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    try:
        result = runScheduleServiceClient.service.findAllRuns()
    except Exception:
        print "Exception ERROR in findRunName"
        print "Unable to contact data servicesl"
        print "Request timed out."
        print "The request timeout for the sent message was reached without receiving a response from the server."
        sys.exit(2)
    except soapFault:
        print "Soap fault ERROR in findRunName"
        print soapFault
        sys.exit(2)
    runArray = result.run
    runName = None
    for run in runArray:

        try:
            if startDate >= run.startTime and endDate <= run.endTime:
                runName = run.runName
                break
        except Exception as ex:
            print "ERROR caught in findRunName:" + str(ex)
            print startDate
            print run.startTime
            print endDate
            print run.endTime
            raise ex
    return runName

def findBeamlineSchedule(beamlineName, runName):
    """Find beamline schedule for given beamlineName and runName"""

    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    try:
        result  = beamlineScheduleServiceClient.service.findBeamlineSchedule(beamlineName, runName)
    except SAXParseException as ex:
        print "ERROR in findBeamlineSchedule\n"
        traceback.print_exc()
        sys.exit(2)

    return result

def findBeamtimeRequestsByBeamline(beamlineName, runName):
    """Find beamline schedule for given beamlineName and runName

    Returns schedule object."""
    try:
        result  = beamlineScheduleServiceClient.service.findBeamtimeRequestsByBeamline(beamlineName, runName)
    except SAXParseException:
        print "ERROR in findBeamtimeRequestsByBeamline"
    except Exception:
        print "ERROR in findBeamtimeRequestByBeamline\n"
        traceback.print_exc()
        sys.exit(2)
    return result

def setup_connection():
    
    home = expanduser("~")
    credentials = os.path.join(home, 'scheduling.ini')
    
    cf = ConfigParser.ConfigParser()
    cf.read(credentials)
    username = cf.get('credentials', 'username')
    password = cf.get('credentials', 'password')
    beamline = cf.get('settings', 'beamline')
    
    # Uncomment one if using ANL INTERNAL or EXTERNAL network
    #base = cf.get('hosts', 'internal')
    base = cf.get('hosts', 'external')

    result = urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))
    logging.raiseExceptions = 0

    beamlineScheduleServiceURL = base + \
         'beamlineScheduleService/beamlineScheduleWebService.wsdl'

    runScheduleServiceURL = base + \
         'runScheduleService/runScheduleWebService.wsdl'

    try:
        credentials = dict(username=username, password=password)
        t = HttpAuthenticated(**credentials)
        if debug:
            print t.u2handlers()
            print t.credentials()
        runScheduleServiceClient = Client(runScheduleServiceURL)
        runScheduleServiceClient.options.cache.setduration(seconds=10)
        result = setSoapHeader(runScheduleServiceClient, username, password)
        beamlineScheduleServiceClient = Client(beamlineScheduleServiceURL)
        beamlineScheduleServiceClient.options.cache.setduration(seconds=10)
        result = setSoapHeader(beamlineScheduleServiceClient, username, password)
    except Exception, ex:
        print "CANNOT OPEN SERVICES:" + str(ex)
        raise
        exit(-1)

    return runScheduleServiceClient, beamlineScheduleServiceClient, beamline

def get_users(date=None):
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
    
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(date, date)
    schedule = findBeamlineSchedule(beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= event.startTime and date <= event.endTime:
                        for experimenter in event.beamtimeRequest.proposal.experimenters.experimenter:
                            for key in experimenter.__keylist__:
                                users[experimenter.lastName][key] = getattr(experimenter, key)
        except:
            ipdb.set_trace()
            raise

    return users

def get_proposal_id(date=None):
    """Find the proposal number (GUP) for a given beamline and date

    Returns proposal id."""

    proposal_id = "empty_proposal_id"
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(date, date)
    schedule = findBeamlineSchedule(beamline, run_name)

    events = schedule.activities.activity

    users = defaultdict(dict)
    for event in events:
        try:
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= event.startTime and date <= event.endTime:
                        proposal_id = event.beamtimeRequest.proposal.id
        except:
            ipdb.set_trace()
            raise

    return proposal_id

def get_proposal_title(date=None):
    """Find the proposal title for a given beamline and date

    Returns proposal title."""

    proposal_title = "empty_proposal_title"
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(date, date)
    schedule = findBeamlineSchedule(beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= event.startTime and date <= event.endTime:
                        proposal_title = event.beamtimeRequest.proposal.proposalTitle
        except:
            ipdb.set_trace()
            raise

    return clean_entry(proposal_title)


def get_experiment_start(date=None):
    """Find the experiment start date for a given beamline and date

    Returns experiment_start."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(date, date)
    schedule = findBeamlineSchedule(beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= event.startTime and date <= event.endTime:
                        experiment_start = event.startTime
        except:
            ipdb.set_trace()
            raise

    return experiment_start


def get_experiment_end(date=None):
    """Find the experiment end date for a given beamline and date

    Returns experiment_end."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(date, date)
    schedule = findBeamlineSchedule(beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= event.startTime and date <= event.endTime:
                        experiment_end = event.endTime
        except:
            ipdb.set_trace()
            raise

    return experiment_end


def get_beamtime_request(date=None):
    """Find the proposal beamtime request id for a given beamline and date

    Returns users."""
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(date, date)
    schedule = findBeamlineSchedule(beamline, run_name)

    events = schedule.activities.activity

    users = defaultdict(dict)
    for event in events:
        try:
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access', 'sector staff']:
                if date >= event.startTime and date <= event.endTime:
                        beamtime_request = event.beamtimeRequest.id
        except:
            ipdb.set_trace()
            raise

    return beamtime_request
    

def create_experiment_id(date=None):
    """
    Generate a unique experiment id as g + GUP # + r + Beamtime Request
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    experiment id       
    """
    
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
   
    # scheduling system settings
    print "\nCrating a unique experiment ID... "
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    proposal_id = get_proposal_id(date.replace(tzinfo=None))
    beamtime_request = get_beamtime_request(date.replace(tzinfo=None))
    
    experiment_id = 'g' + str(proposal_id) + 'r' + str(beamtime_request)

    return experiment_id

def find_experiment_info(date=None):
    """
    Generate a unique experiment id as g + GUP # + r + Beamtime Request
     
    Parameters
    ----------
    date : date
        Experiment date
    
    Returns
    -------
    experiment id       
    """
       
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
   
    # scheduling system settings
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    proposal_id = get_proposal_id(date.replace(tzinfo=None))
    proposal_title = get_proposal_title(date.replace(tzinfo=None))
    #print proposal_id, proposal_title
    
    return str(proposal_id), str(proposal_title[:256])

def find_experiment_start(date=None):
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

    datetime_format = '%Y-%m-%dT%H:%M:%S%z'

    # scheduling system settings
    print "\nFinding experiment start date ... "
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()

    experiment_start = get_experiment_start(date.replace(tzinfo=None))
 
    return experiment_start
    

def find_users(date=None):
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

    print "\nFinding users ... "
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    users = get_users(date.replace(tzinfo=None))
    
    return users


def find_pi_last_name(date=None):
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
    print "\nFinding PI last name ... "
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    users = get_users(date.replace(tzinfo=None))

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
            name = str(users[tag]['firstName'] + ' ' + users[tag]['lastName'])            
            role = "*"
            institution = str(strip_accents(users[tag]['institution']))
            badge = str(users[tag]['badge'])
            email = str(users[tag]['email'])
            print "", role, badge, name, institution, email
        else:            
            print "", users[tag]['badge'], users[tag]['firstName'], users[tag]['lastName'], strip_accents(users[tag]['institution']), users[tag]['email']
    print "(*) Proposal PI"        


def find_pi_info(date=None):
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
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()
    users = get_users(date.replace(tzinfo=None))

    pi_name = "empty_pi_name"
    pi_institution = "empty_pi_institution"
    pi_badge = "empty_pi_badge" 
    pi_email = "empty_pi_email"

    for tag in users:
        if users[tag].get('piFlag') != None:
            pi_name = str(strip_accents(users[tag]['firstName']) + ' ' + strip_accents(users[tag]['lastName']))            
            pi_role = "*"
            pi_institution = str(strip_accents(users[tag]['institution']))
            pi_badge = str(users[tag]['badge'])
            pi_email = str(users[tag]['email'])
    
    return pi_name, pi_institution[:256], pi_badge, pi_email      


def print_experiment_info(date=None):
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
    print "Inputs: "
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
    print "\tTime of Day: ", date.strftime(datetime_format)
    print "\tBeamline: ", beamline

    # scheduling system settings
    print "\n\tAccessing the APS Scheduling System ... "
    runScheduleServiceClient, beamlineScheduleServiceClient, beamline = setup_connection()

    run_name = findRunName(now.replace(tzinfo=None), now.replace(tzinfo=None))
    proposal_title = get_proposal_title(date.replace(tzinfo=None))
    users = get_users(beamline, date.replace(tzinfo=None))
    experiment_start = get_experiment_start(date.replace(tzinfo=None))
    experiment_end = get_experiment_end(date.replace(tzinfo=None))

    print "\tRun Name: ", run_name 
    print "\n\tProposal Title: ", proposal_title
    print "\tExperiment Start: ", experiment_start
    print "\tExperiment End: ", experiment_end
    # print user emails
    print "\n\tUser email address: "
    for tag in users:
        if users[tag].get('email') != None:
            email = str(users[tag]['email'])
            print "\t\t", email
        else:            
            print "\tMissing e-mail for:", users[tag]['badge'], users[tag]['firstName'], users[tag]['lastName'], strip_accents(users[tag]['institution'])


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
    utf_8_str = unicode(entry) 
    norml_str = unicodedata.normalize('NFKD', utf_8_str)
    cleaned_folder_name = norml_str.encode('ASCII', 'ignore')
        
    return ''.join(c for c in cleaned_folder_name if c in valid_folder_entry_chars)

