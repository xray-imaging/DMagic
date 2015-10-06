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
Module for describing beamline/experiment specific data recipes.
"""

import os
import pytz
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

from validate_email import validate_email

__author__ = "Francesco De Carlo"
__credits__ = "John Hammonds"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['findRunName',
           'findBeamlineSchedule',
           'get_users']

debug = False

""" You must use the APS web password. You can check it by logging into
the proposal system. Be careful because this system also accepts LDAP
account info.

The credentials are stored in a '.ini' file and read by python.
 - Create a file called 'credentials.ini',
 - Put the following text in it:
 [credentials]
 username = YOUR BADGE NUMBER
 password = YOUR APS WEB PASSWORD

 [hosts]
 internal = https: ....
 external = https: .... 
 
 that's it.

"""

cf = ConfigParser.ConfigParser()
cf.read('credentials.ini')
username = cf.get('credentials', 'username')
password = cf.get('credentials', 'password')

# Uncomment one if using ANL INTERNAL or EXTERNAL network
#base = cf.get('hosts', 'internal')
base = cf.get('hosts', 'external')

# see README.txt to set a globus personal shared folder
cf = ConfigParser.ConfigParser()
cf.read('globus.ini')
globus_address = cf.get('settings', 'cli_address')
globus_user = cf.get('settings', 'cli_user')
beamline = cf.get('settings', 'beamline')
scp_options = cf.get('settings', 'scp_options')

local_user = cf.get('globus connect personal', 'user') 
local_share1 = cf.get('globus connect personal', 'share1') 
local_share2 = cf.get('globus connect personal', 'share2') 
local_shared_folder = cf.get('globus connect personal', 'shared_folder')  

remote_user = cf.get('globus remote server', 'user') 
remote_share = cf.get('globus remote server', 'share') 
remote_shared_folder = cf.get('globus remote server', 'shared_folder')  

globus_ssh = "ssh " + globus_user + globus_address

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
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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

    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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

    return runScheduleServiceClient, beamlineScheduleServiceClient

def get_users(beamline='2-BM-A,B', date=None):
    """
    Get users running at beamline at a specific date 
    Parameters
    ----------
    beamline : str
        APS beamline.
    date : date
        Experiment date
    Returns
    -------
    users        
    """
    
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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

def get_proposal_id(beamline='2-BM-A,B', date=None):
    """Find the proposal number (GUP) for a given beamline and date

    Returns users."""
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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

def get_proposal_title(beamline='2-BM-A,B', date=None):
    """Find the proposal title for a given beamline and date

    Returns users."""
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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

    return proposal_title

def get_experiment_start(beamline='2-BM-A,B', date=None):
    """Find the experiment start date for a given beamline and date

    Returns experiment_start."""
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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

def get_experiment_end(beamline='2-BM-A,B', date=None):
    """Find the experiment end date for a given beamline and date

    Returns experiment_end."""
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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

def get_beamtime_request(beamline='2-BM-A,B', date=None):
    """Find the proposal beamtime request id for a given beamline and date

    Returns users."""
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
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
    
def create_experiment_id(beamline='2-BM-A,B', date=None):
    
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
   
    # scheduling system settings
    print "\n\tAccessing the APS Scheduling System ... "
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
    proposal_id = get_proposal_id(beamline, date.replace(tzinfo=None))
    beamtime_request = get_beamtime_request(beamline, date.replace(tzinfo=None))
    
    experiment_id = 'g' + str(proposal_id) + 'r' + str(beamtime_request)
    print "\tUnique experiment ID: ",  experiment_id     

    return experiment_id

def list_experiment_info(beamline='2-BM-A,B', date=None):
    print "Inputs: "
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
    print "\tTime of Day: ", date.strftime(datetime_format)
    print "\tBeamline: ", beamline

    # scheduling system settings
    print "\n\tAccessing the APS Scheduling System ... "
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()

    run_name = findRunName(now.replace(tzinfo=None), now.replace(tzinfo=None))
    proposal_title = get_proposal_title(beamline, date.replace(tzinfo=None))
    users = get_users(beamline, date.replace(tzinfo=None))
    experiment_start = get_experiment_start(beamline, date.replace(tzinfo=None))
    experiment_end = get_experiment_end(beamline, date.replace(tzinfo=None))

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
            print "\tMissing e-mail for:", users[tag]['badge'], users[tag]['firstName'], users[tag]['lastName'], users[tag]['institution']

def find_experiment_start(beamline='2-BM-A,B', date=None):

    datetime_format = '%Y-%m-%dT%H:%M:%S%z'

    # scheduling system settings
    print "\n\tAccessing the APS Scheduling System ... "
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()

    experiment_start = get_experiment_start(beamline, date.replace(tzinfo=None))
    print "\tExperiment Start: ", experiment_start
 
    return experiment_start
    
def find_users(beamline='2-BM-A,B', date=None):
    # scheduling system settings
    print "\n\tAccessing the APS Scheduling System ... "
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()

    users = get_users(beamline, date.replace(tzinfo=None))

    # find the Principal Investigator
    for tag in users:
        if users[tag].get('piFlag') != None:
            name = str(users[tag]['firstName'] + ' ' + users[tag]['lastName'])            
            role = "*"
            institution = str(users[tag]['institution'])
            badge = str(users[tag]['badge'])
            email = str(users[tag]['email'])
            print "\t\t", role, badge, name, institution, email
        else:            
            print "\t\t", users[tag]['badge'], users[tag]['firstName'], users[tag]['lastName'], users[tag]['institution'], users[tag]['email']
    print "\t(*) Proposal PI"        
    
    return users

def create_unique_directory(exp_start, exp_id):
    
    datetime_format = '%Y-%m'
    unique_directory = local_shared_folder + str(exp_start.strftime(datetime_format)) + os.sep + exp_id

    if os.path.exists(unique_directory) == False: 
        os.makedirs(unique_directory)    
        print "\n\tCreating unique data directory: ", unique_directory
    else:
        print "\n\tDirectory already exists: ", unique_directory
    
    return unique_directory

def globus_local_share(directory, users):

    path_list = directory.split(os.sep)
    data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep

    print "\n\tSend a token to share the globus connect personal folder called: ", data_share
    for tag in users:
        if users[tag].get('email') != None:
            email = str(users[tag]['email'])
            globus_add = "acl-add " + local_user + local_share1 + os.sep + data_share  + " --perm r --email " + email
            if validate_email(email) and os.path.isdir(directory):
                cmd = "ssh " + globus_user + globus_address + " " + globus_add
                print cmd

    # for demo
    email = 'decarlo@aps.anl.gov'
    globus_add = "acl-add " + local_user + local_share1 + os.sep + data_share  + " --perm r --email " + email
    cmd = "ssh " + globus_user + globus_address + " " + globus_add
    #print "ssh decarlo@cli.globusonline.org acl-add decarlo#data/2014-10/g40065r94918/ --perm r --email decarlof@gmail.com"
    print cmd
    #os.system(cmd)
    print "\n\n=================================================================="
    print "Check your email to download the data from globus connect personal"
    print "=================================================================="

def globus_cp(directory, users):
        
    path_list = directory.split(os.sep)
    data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep

    globus_scp = "scp -r " + local_user + local_share1 + ":" + os.sep + data_share + " " + remote_user + remote_share + ":" + remote_shared_folder
    if os.path.isdir(directory):
        cmd = "ssh " + globus_user + globus_address + " " + globus_scp + " " + scp_options
        #print "ssh decarlo@cli.globusonline.org scp -r decarlo#data:/txm/ petrel#tomography:dm/"
        print cmd
        #os.system(cmd1)
        print "Done data trasfer to: ", remote_user
       
if __name__ == "__main__":

    # Input parameters
    #now = datetime.datetime.now(pytz.timezone('US/Central'))
    now = datetime.datetime(2014, 10, 18, 10, 10, 30).replace(tzinfo=pytz.timezone('US/Central'))

    print "Input (experiment date): ", now
    #list_experiment_info(beamline, now)
    exp_id = create_experiment_id(beamline, now)
    exp_start = find_experiment_start(beamline, now)
                      
    unique_directory = create_unique_directory(exp_start, exp_id)

    users = find_users(beamline, now)
    globus_local_share(unique_directory, users)
    globus_cp(unique_directory, users)
