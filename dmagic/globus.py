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
Module containing basic functions to use the 
`Globus CLI <http://dev.globus.org/cli/>`__

You must create in your home directory the 
`globus.ini <https://github.com/decarlof/data-management/blob/master/config/globus.ini>`__ 
configuration file

Functions with the dm prefix are specific to Data Management tasks and are designed to be
integrated with the beamline data collection software

"""

import os
import sys
from os.path import expanduser
import ConfigParser
from validate_email import validate_email
import dmagic.react as react

__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['dm_create_directory',
           'dm_monitor',
           'dm_settings',
           'dm_share',
           'dm_upload',
           'upload']

def dm_create_directory(exp_start, exp_id, mode = 'local'):
    """
    Create a unique directory based on experiment starting date and activity number
     
    Parameters
    ----------
    exp_start : date
        Experiment staring date
    
    exp_id : str
        Unique experiment id
        
    globus : str
        None, remote, personal

    Returns
    -------
    Full directory path under the shared Endpoint        
    """
    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)

    globus_user = cf.get('settings', 'cli_user')
    globus_address = cf.get('settings', 'cli_address')   
    globus_ssh = "ssh " + globus_user + globus_address

    datetime_format = '%Y-%m'
    
    if (mode == 'local'):   
        local_folder = cf.get('local host', 'folder')  
        unique_directory = local_folder + str(exp_start.strftime(datetime_format)) + os.sep + exp_id
        if os.path.exists(unique_directory) == False: 
            os.makedirs(unique_directory)    
            print "\nCreating unique local data directory: ", unique_directory
        else:
            print "\nLocal data directory already exists: ", unique_directory
    else:
        unique_directory ='' 
        if (mode == 'personal'):
            user = cf.get('globus connect personal', 'user') 
            host = '#' + cf.get('globus connect personal', 'host') 
            share = cf.get('globus connect personal', 'share') 
            folder = cf.get('globus connect personal', 'folder')  
            globus_mkdir1 = 'mkdir ' +  user + share + ":" + os.sep + '~' + os.sep + str(exp_start.strftime(datetime_format)) + os.sep        
            globus_mkdir2 = 'mkdir ' +  user + share + ":" + os.sep + '~' + os.sep + str(exp_start.strftime(datetime_format)) + os.sep + exp_id + os.sep       
        elif (mode == 'remote'):
            user = cf.get('globus remote server', 'user') 
            host = '#' + cf.get('globus remote server', 'host') 
            share = cf.get('globus remote server', 'share') 
            folder = cf.get('globus remote server', 'folder')  
            globus_mkdir1 = 'mkdir ' +  user + share + ":" + folder + str(exp_start.strftime(datetime_format)) + os.sep        
            globus_mkdir2 = 'mkdir ' +  user + share + ":" + folder + str(exp_start.strftime(datetime_format)) + os.sep + exp_id + os.sep       

        cmd1 = globus_ssh + " " + globus_mkdir1
        cmd2 = globus_ssh + " " + globus_mkdir2
        os.system(cmd1)
        os.system(cmd2)
        print cmd1
        print cmd2
        
    return unique_directory


def dm_settings():
    """
    Print the current Globus settings. Edit ~/.globus.ini to match your configuration
    """
    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)
    globus_address = cf.get('settings', 'cli_address')
    globus_user = cf.get('settings', 'cli_user')

    personal_user = cf.get('globus connect personal', 'user') 
    personal_host = cf.get('globus connect personal', 'host') 
    personal_share = cf.get('globus connect personal', 'share') 
    personal_folder = cf.get('globus connect personal', 'folder')  
    
    remote_user = cf.get('globus remote server', 'user') 
    remote_host = cf.get('globus remote server', 'host') 
    remote_share = cf.get('globus remote server', 'share') 
    remote_folder = cf.get('globus remote server', 'folder')  
    
    globus_ssh = "ssh " + globus_user + globus_address
    print "\n\nCurrent Globus Settings:"

    print "\tCLI user: ", globus_user
    print "\tCLI address: ", globus_address
    print "\tCLI ssh: ", globus_ssh

    print "Globus Connect Personal Configuration: "
    print "\tGlobus User: ", personal_user
    print "\tPersonal Host: ", personal_host
    print "\tPersonal share: ", personal_share
    print "\tPersonal folder under data management: " + personal_folder 

    print "Globus Server Configuration: "
    print "\tRemote Host: ", remote_host

    print "\tRemote Share: " + remote_user + remote_share
    print "\tRemote folder under data management: " + remote_folder 
    print "\nEdit globus.ini to match your globus configuration"

def dm_monitor(directory, protocol='scp'):
    """
    Monitor a directory on the data collection machine and automatically copy 
    the raw data to the data analysis machine where the Globus Connect Personal 
    Endpoint is running. 
         
    Parameters
    ----------
    directory : str
        Unique directory shared by the Globus Connect Personal Endpoint
    
    protocol : str
        copy protocol. scp (default), ... 
    """
    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)

    local_user = cf.get('local host', 'user') 
    local_host = cf.get('local host', 'host') 
    local_folder = cf.get('local host', 'folder')  

    personal_user = cf.get('globus connect personal', 'user') 
    personal_host = cf.get('globus connect personal', 'host') 
    personal_folder = cf.get('globus connect personal', 'folder')  

    path_list = directory.split(os.sep)
    personal_path = personal_folder + path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]

    cmd = 'scp ' + '$f ' + personal_host + ':' + personal_path 
    # start directory monitoring
    sys.argv  = ['react', directory, '-p', '*.hdf', cmd]
    print "\nStart raw data monitoring:" 
    print "\tserver: ", local_host
    print "\tdirectory: ", directory
    print "\nNew files will be copied to: " 
    print "\tserver: ", personal_host
    print "\tdirectory: ", personal_path

    print "\nControl-C to exit"
    react.main(sys.argv)

def dm_upload(directory):
    """
    Upload the unique directory under the Globus Connect Personal Endpoint 
    that is autoamatically generated by the scheduling system
    to the remote Globus Server
     
    Parameters
    ----------
    directory : str
        Unique directory shared by the Globus Connect Personal Endpoint
    
    """
        
    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)
    globus_user = cf.get('settings', 'cli_user')
    globus_address = cf.get('settings', 'cli_address')   
    globus_ssh = "ssh " + globus_user + globus_address

    scp_options = cf.get('settings', 'scp_options')

    cmd1 = -1
    cmd2 = -1
    
    personal_user = cf.get('globus connect personal', 'user') 
    personal_host = '#' + cf.get('globus connect personal', 'host') 
    personal_folder = cf.get('globus connect personal', 'folder')  
   
    remote_user = cf.get('globus remote server', 'user') 
    remote_host = '#' + cf.get('globus remote server', 'host') 
    remote_share = cf.get('globus remote server', 'share') 
    remote_folder = cf.get('globus remote server', 'folder')  
    
    path_list = directory.split(os.sep)
    personal_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep 
    personal_date_folder = path_list[len(path_list)-2]

    path_list = remote_folder.split(os.sep)
    remote_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]

    globus_mkdir = 'mkdir ' +  remote_user + remote_share + ":" + remote_folder + personal_date_folder + os.sep        
    globus_scp = "scp -r " + personal_user + personal_host + ":" + personal_folder + personal_data_share + " " + remote_user + remote_share + ":" + os.sep + remote_data_share + personal_date_folder + os.sep 

    if os.path.isdir(directory):
        cmd1 = globus_ssh + " " + globus_mkdir
        cmd2 = globus_ssh + " " + globus_scp + " " + scp_options

    return cmd1, cmd2
       
      
def dm_share(directory, users, mode):
    """
    Send an e-mail to users with a link to access the unique experiment 
    directory under the Globus personal/remote Endpoint that is autoamatically 
    generated by the scheduling system
     
    Parameters
    ----------
    directory : str
        Unique directory created by the scheduling system.
    
    users : dictionary-like object containing user information      
    
    mode : str
        personal/remote Endpoint hosting the share 

    Returns
    -------
    cmd : list 
        Globus Command Line strings. If executed with os.system() 
        will send notification e-mail to user         
    """

    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)
    globus_address = cf.get('settings', 'cli_address')
    globus_user = cf.get('settings', 'cli_user')
    globus_ssh = "ssh " + globus_user + globus_address

    cmd = []    
    if mode == 'personal':
        user = cf.get('globus connect personal', 'user') 
        share = cf.get('globus connect personal', 'share')
        folder = cf.get('globus connect personal', 'folder')
        path_list = directory.split(os.sep)
        data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep
        end_point_share = user + share + os.sep + data_share
        for tag in users:
            if users[tag].get('email') != None:
                email = str(users[tag]['email'])
                globus_add = "acl-add " + end_point_share + " --perm r --email " + email
                if validate_email(email) and os.path.isdir(directory):
                    cmd.append(globus_ssh + " " + globus_add)

    elif mode == 'remote': 
        user = cf.get('globus remote server', 'user')
        share = cf.get('globus remote server', 'share')
        folder = cf.get('globus remote server', 'folder')
        path_list = directory.split(os.sep)
        data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep
        end_point_share = user + share + os.sep + data_share
        for tag in users:
            if users[tag].get('email') != None:
                email = str(users[tag]['email'])
                globus_add = "acl-add " + end_point_share + " --perm r --email " + email
                if validate_email(email):
                    cmd.append(globus_ssh + " " + globus_add)

    return cmd
    

def upload(directory):
    """
    Upload a directory under the Globus Connect Personal Endpoint 
    to the remote Globus Server
     
    Parameters
    ----------
    directory : str
        Directory under the Globus Connect Personal Endpoint share
    
    """
        
    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)

    globus_address = cf.get('settings', 'cli_address')
    globus_user = cf.get('settings', 'cli_user')
    scp_options = cf.get('settings', 'scp_options')
    
    personal_user = cf.get('globus connect personal', 'user') 
    personal_host = '#' + cf.get('globus connect personal', 'host') 
    personal_folder = cf.get('globus connect personal', 'folder')  
   
    remote_user = cf.get('globus remote server', 'user') 
    remote_share = cf.get('globus remote server', 'share') 
    remote_folder = cf.get('globus remote server', 'folder')  
    
    globus_ssh = "ssh " + globus_user + globus_address

    globus_scp = "scp -r " + personal_user + personal_host + ":" + personal_folder + directory + " " + remote_user + remote_share + ":" + remote_folder 

    if os.path.isdir(personal_folder + directory):
        cmd = globus_ssh + " " + globus_scp + " " + scp_options
        return cmd
    else:
        return -1

