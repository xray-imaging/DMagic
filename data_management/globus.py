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
"""

import os
from os.path import expanduser
import ConfigParser
from validate_email import validate_email

__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

home = expanduser("~")
globus = os.path.join(home, 'globus.ini')

# see README.txt to set a globus personal shared folder
cf = ConfigParser.ConfigParser()
cf.read(globus)
globus_address = cf.get('settings', 'cli_address')
print globus_address
globus_user = cf.get('settings', 'cli_user')
scp_options = cf.get('settings', 'scp_options')

local_user = cf.get('globus connect personal', 'user') 
local_host = cf.get('globus connect personal', 'host') 
local_share1 = cf.get('globus connect personal', 'share1') 
local_share2 = cf.get('globus connect personal', 'share2') 
local_folder = cf.get('globus connect personal', 'folder')  

remote_user = cf.get('globus remote server', 'user') 
remote_host = cf.get('globus remote server', 'host') 
remote_share = cf.get('globus remote server', 'share') 
remote_folder = cf.get('globus remote server', 'folder')  

globus_ssh = "ssh " + globus_user + globus_address


def create_unique_directory(exp_start, exp_id):
    
    datetime_format = '%Y-%m'
    unique_directory = local_folder + str(exp_start.strftime(datetime_format)) + os.sep + exp_id

    if os.path.exists(unique_directory) == False: 
        os.makedirs(unique_directory)    
        print "\nCreating unique data directory: ", unique_directory
    else:
        print "\nDirectory already exists: ", unique_directory
    
    return unique_directory

def settings():
    
    print "\n\nCurrent Globus Settings:"

    print "\tCLI user: ", globus_user
    print "\tCLI address: ", globus_address
    #print scp_options

    print "Globus Connect Personal Configuration: "
    print "\tGlobus User: ", local_user
    print "\tLocal Host: ", local_host
    print "\tLocal Share1: " + local_user + local_share1 + "; Host Endpoint: " + local_folder + " on " + local_user + "#" + local_host
    print "\tLocal Share1 is used to upload data to a remote server"
    print "\tLocal Share2: " + local_user + local_share2 + "; Host Endpoint: " + remote_folder + " on " + remote_user + "#" + remote_host
    print "\tLocal Share2 is used to share data on the remote server with users"
    print "Globus Server Configuration: "
    print "\tRemote Host: ", remote_host

    path_list = remote_folder.split(os.sep)
    remote_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]
    print "\tRemote Share: " + remote_user + remote_share + "; sharing the remote folder: " + remote_data_share 

    print "\n\tEdit globus.ini to match your globus configuration"

def upload(local_directory):
        
    path_list = local_directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep 
    local_date_folder = path_list[len(path_list)-2]

    path_list = remote_folder.split(os.sep)
    remote_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]

    globus_mkdir = 'mkdir ' +  remote_user + remote_share + ":" + os.sep + remote_data_share + local_date_folder + os.sep        
    globus_scp = "scp -r " + local_user + local_share1 + ":" + os.sep + local_data_share + " " + remote_user + remote_share + ":" + os.sep + remote_data_share + local_date_folder + os.sep 

    if os.path.isdir(local_directory):
        cmd1 = globus_ssh + " " + globus_mkdir
        cmd2 = globus_ssh + " " + globus_scp + " " + scp_options
        #print "ssh decarlo@cli.globusonline.org scp -r decarlo#data:/txm/ petrel#tomography:dm/"
        print cmd1
        print cmd2
        
        #os.system(cmd1)
        print "Done data trasfer to: ", remote_user
       
def share_local(directory, users):

    path_list = directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep

    print "\n\tSend a token to share the globus connect personal folder: ", local_data_share
    for tag in users:
        if users[tag].get('email') != None:
            email = str(users[tag]['email'])
            globus_add = "acl-add " + local_user + local_share1 + os.sep + local_data_share  + " --perm r --email " + email
            if validate_email(email) and os.path.isdir(directory):
                cmd = globus_ssh + " " + globus_add
                print "\nEmail sent to: ", email
                print cmd
                #os.system(cmd)

    # for demo
    email = 'decarlof@gmail.com'
    globus_add = "acl-add " + local_user + local_share1 + os.sep + local_data_share  + " --perm r --email " + email
    cmd = globus_ssh + " " + globus_add
    #print "ssh decarlo@cli.globusonline.org acl-add decarlo#data/2014-10/g40065r94918/ --perm r --email decarlof@gmail.com"
    print "\nEmail sent to: ", email
    print cmd
    #os.system(cmd)
    return cmd
      
def share_remote(directory, users):

    path_list = directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep

    print "\n\tSend a token to share the globus server folder: ", local_data_share
    for tag in users:
        if users[tag].get('email') != None:
            email = str(users[tag]['email'])
            globus_add = "acl-add " + local_user + local_share2 + os.sep + local_data_share  + " --perm r --email " + email
            if validate_email(email) and os.path.isdir(directory):
                cmd = globus_ssh + " " + globus_add
                print "\nEmail sent to: ", email
                print cmd
                #os.system(cmd)

    # for demo
    email = 'decarlof@gmail.com'
    globus_add = "acl-add " + local_user + local_share2 + os.sep + local_data_share  + " --perm r --email " + email
    cmd = globus_ssh + " " + globus_add
    #print "ssh decarlo@cli.globusonline.org acl-add decarlo#data/2014-10/g40065r94918/ --perm r --email decarlof@gmail.com"
    print "\nEmail sent to: ", email
    print cmd
    #os.system(cmd)
    return cmd
      
