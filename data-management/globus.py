# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 16:55:08 2015

@author: decarlo
"""
import os
import ConfigParser
from validate_email import validate_email

# see README.txt to set a globus personal shared folder
cf = ConfigParser.ConfigParser()
cf.read('globus2.ini')
globus_address = cf.get('settings', 'cli_address')
globus_user = cf.get('settings', 'cli_user')
scp_options = cf.get('settings', 'scp_options')

local_user = cf.get('globus connect personal', 'user') 
local_host = cf.get('globus connect personal', 'host') 
local_share1 = cf.get('globus connect personal', 'share1') 
local_share2 = cf.get('globus connect personal', 'share2') 
local_shared_folder = cf.get('globus connect personal', 'shared_folder')  

remote_user = cf.get('globus remote server', 'user') 
remote_host = cf.get('globus remote server', 'host') 
remote_share = cf.get('globus remote server', 'share') 
remote_shared_folder = cf.get('globus remote server', 'shared_folder')  

globus_ssh = "ssh " + globus_user + globus_address


def create_unique_directory(exp_start, exp_id):
    
    datetime_format = '%Y-%m'
    unique_directory = local_shared_folder + str(exp_start.strftime(datetime_format)) + os.sep + exp_id

    if os.path.exists(unique_directory) == False: 
        os.makedirs(unique_directory)    
        print "\nCreating unique data directory: ", unique_directory
    else:
        print "\nDirectory already exists: ", unique_directory
    
    return unique_directory

def local_share(directory, users):

    path_list = directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep

    print "\n\tSend a token to share the globus connect personal folder called: ", local_data_share
    for tag in users:
        if users[tag].get('email') != None:
            email = str(users[tag]['email'])
            globus_add = "acl-add " + local_user + local_share1 + os.sep + local_data_share  + " --perm r --email " + email
            if validate_email(email) and os.path.isdir(directory):
                cmd = "ssh " + globus_user + globus_address + " " + globus_add
                print cmd

    # for demo
    email = 'decarlo@aps.anl.gov'
    globus_add = "acl-add " + local_user + local_share1 + os.sep + local_data_share  + " --perm r --email " + email
    cmd = "ssh " + globus_user + globus_address + " " + globus_add
    #print "ssh decarlo@cli.globusonline.org acl-add decarlo#data/2014-10/g40065r94918/ --perm r --email decarlof@gmail.com"
    print cmd
    #os.system(cmd)
    print "\n\n=================================================================="
    print "Check your email to download the data from globus connect personal"
    print "=================================================================="

def settings():
    
    print "Edit globus2.ini to match your globus configuration"
    print "Current Globus Settings:"

    print "\tCLI user: ", globus_user
    print "\tCLI address: ", globus_address
    #print scp_options

    print "Make sure Globus Connect Personal is running on your local machine with the following configuration: "
    print "\tUser: ", local_user
    print "\tShare: " + local_user + local_share1 + "; sharing the local folder: " + local_shared_folder + " on " + local_user + local_host

    print "\tShare: " + local_user + local_share2 + "; sharing the remote folder: " + remote_shared_folder + " on " + remote_user + remote_host
    


def upload(local_directory, remote_directory):
        
    path_list = local_directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep    
    
    path_list = remote_shared_folder.split(os.sep)
    remote_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]
    
    globus_scp = "scp -r " + local_user + local_share1 + ":" + os.sep + local_data_share + " " + remote_user + remote_share + ":" + os.sep + remote_data_share
    if os.path.isdir(local_directory):
        cmd = "ssh " + globus_user + globus_address + " " + globus_scp + " " + scp_options
        #print "ssh decarlo@cli.globusonline.org scp -r decarlo#data:/txm/ petrel#tomography:dm/"
        print cmd
        #os.system(cmd1)
        print "Done data trasfer to: ", remote_user
       
