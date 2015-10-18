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
Module containing basic routines to use globus CLI

You must create in your home directory the 
`globus.ini <https://github.com/decarlof/data-management/blob/master/config/globus.ini>`__ 
configuration file

"""

import os
from os.path import expanduser
import ConfigParser
from validate_email import validate_email

__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['dm_create_directory',
           'dm_settings',
           'dm_share',
           'dm_upload',
           'share',
           'upload']

def dm_create_directory(exp_start, exp_id):
    """
    Create a unique directory based on experiment starting date and activity number
     
    Parameters
    ----------
    exp_start : date
        Experiment staring date
    
    exp_id : str
        Unique experiment id

    Returns
    -------
    Full directory path under the shared Endpoint        
    """

    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)
    local_folder = cf.get('globus connect personal', 'folder')  
    
    datetime_format = '%Y-%m'
    unique_directory = local_folder + str(exp_start.strftime(datetime_format)) + os.sep + exp_id

    if os.path.exists(unique_directory) == False: 
        os.makedirs(unique_directory)    
        print "\nCreating unique data directory: ", unique_directory
    else:
        print "\nDirectory already exists: ", unique_directory
    
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

    local_user = cf.get('globus connect personal', 'user') 
    local_host = '#' + cf.get('globus connect personal', 'host') 
    local_share = cf.get('globus connect personal', 'share') 
    local_folder = cf.get('globus connect personal', 'folder')  
    
    remote_user = cf.get('globus remote server', 'user') 
    remote_host = '#' + cf.get('globus remote server', 'host') 
    remote_share = cf.get('globus remote server', 'share') 
    remote_folder = cf.get('globus remote server', 'folder')  
    
    globus_ssh = "ssh " + globus_user + globus_address
    print "\n\nCurrent Globus Settings:"

    print "\tCLI user: ", globus_user
    print "\tCLI address: ", globus_address
    print "\tCLI ssh: ", globus_ssh

    print "Globus Connect Personal Configuration: "
    print "\tGlobus User: ", local_user
    print "\tLocal Host: ", local_host
    print "\tLocal share: ", local_share
    print "\tLocal folder under data management: " + local_folder 

    print "Globus Server Configuration: "
    print "\tRemote Host: ", remote_host

    print "\tRemote Share: " + remote_user + remote_share
    print "\tRemote folder under data management: " + remote_folder 
    print "\nEdit globus.ini to match your globus configuration"

def dm_upload(directory):
    """
    Upload the unique local directory under the Globus Connect Endpoint 
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
    globus_address = cf.get('settings', 'cli_address')

    globus_user = cf.get('settings', 'cli_user')
    scp_options = cf.get('settings', 'scp_options')
    
    local_user = cf.get('globus connect personal', 'user') 
    local_host = '#' + cf.get('globus connect personal', 'host') 
    local_folder = cf.get('globus connect personal', 'folder')  
   
    remote_user = cf.get('globus remote server', 'user') 
    remote_host = '#' + cf.get('globus remote server', 'host') 
    remote_share = cf.get('globus remote server', 'share') 
    remote_folder = cf.get('globus remote server', 'folder')  
    
    globus_ssh = "ssh " + globus_user + globus_address

    path_list = directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep 
    local_date_folder = path_list[len(path_list)-2]

    path_list = remote_folder.split(os.sep)
    remote_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]

    globus_mkdir = 'mkdir ' +  remote_user + remote_share + ":" + remote_folder + local_date_folder + os.sep        
    globus_scp = "scp -r " + local_user + local_host + ":" + local_folder + local_data_share + " " + remote_user + remote_share + ":" + os.sep + remote_data_share + local_date_folder + os.sep 

    if os.path.isdir(directory):
        cmd1 = globus_ssh + " " + globus_mkdir
        cmd2 = globus_ssh + " " + globus_scp + " " + scp_options
        return cmd1, cmd2
       
      
def dm_share(directory, users, mode):
    """
    Send a token email to users to share the unique local directory 
    under the Globus local/remote Endpoint that is autoamatically 
    generated by the scheduling system
     
    Parameters
    ----------
    directory : str
        Unique directory created by the scheduling system.
    
    users : dictionary-like object containing user information      
    
    mode : str
        local/remote Endpoint hosting the share 

    Returns
    -------
    Globlus Command Line string         
    """

    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)
    globus_address = cf.get('settings', 'cli_address')
    globus_user = cf.get('settings', 'cli_user')
    globus_ssh = "ssh " + globus_user + globus_address
     
    if mode == 'local':
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
                    cmd = globus_ssh + " " + globus_add
                    return cmd
                        
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
                    cmd = globus_ssh + " " + globus_add
                    return cmd

def share(directory, email, mode):
    """
    Send a token email to share a directory under the local or remote Globus Endpoint
     
    Parameters
    ----------
    directory : str
        Full directory path under the Globus Shared Endpoint
        
    email : email
        User email address

    mode : str
        local, remote. Shared folder is on local/remote Endpoint 
    
    Returns
    -------
    Globlus Command Line string         
    """

    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)
    globus_address = cf.get('settings', 'cli_address')
    globus_user = cf.get('settings', 'cli_user')
    globus_ssh = "ssh " + globus_user + globus_address

    if mode == 'local':
        user = cf.get('globus connect personal', 'user') 
        share = cf.get('globus connect personal', 'share')
        folder = cf.get('globus connect personal', 'folder')

        if os.path.isdir(folder + directory) and validate_email(email):
            globus_add = "acl-add " + user + share + os.sep + directory  + " --perm r --email " + email        
            cmd = globus_ssh + " " + globus_add
            return cmd
        else:
            if not validate_email(email):
                return -1
            else:
                return -2
            
    elif mode == 'remote': 
        user = cf.get('globus remote server', 'user')
        share = cf.get('globus remote server', 'share')
        folder = cf.get('globus remote server', 'folder')
    
        if validate_email(email):
            globus_add = "acl-add " + user + share + os.sep + directory  + " --perm r --email " + email        
            cmd = globus_ssh + " " + globus_add
            return cmd
        else:
            return -1
            

def upload(directory):
    """
    Upload a local directory under the Globus Connect Endpoint 
    to the remote Globus Server
     
    Parameters
    ----------
    directory : str
        Directory under the shared by the Globus Connect Personal Endpoint
    
    """
        
    home = expanduser("~")
    globus = os.path.join(home, 'globus.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(globus)

    globus_address = cf.get('settings', 'cli_address')
    globus_user = cf.get('settings', 'cli_user')
    scp_options = cf.get('settings', 'scp_options')
    
    local_user = cf.get('globus connect personal', 'user') 
    local_host = '#' + cf.get('globus connect personal', 'host') 
    local_folder = cf.get('globus connect personal', 'folder')  
   
    remote_user = cf.get('globus remote server', 'user') 
    remote_share = cf.get('globus remote server', 'share') 
    remote_folder = cf.get('globus remote server', 'folder')  
    
    globus_ssh = "ssh " + globus_user + globus_address

    globus_scp = "scp -r " + local_user + local_host + ":" + local_folder + directory + " " + remote_user + remote_share + ":" + remote_folder 

    if os.path.isdir(local_folder + directory):
        cmd = globus_ssh + " " + globus_scp + " " + scp_options
        return cmd
    else:
        return -1

