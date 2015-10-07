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
    
    print "Edit globus2.ini to match your globus configuration"
    print "Current Globus Settings:"

    print "\tCLI user: ", globus_user
    print "\tCLI address: ", globus_address
    #print scp_options

    print "Make sure Globus Connect Personal is running on your local machine with the following configuration: "
    print "\tGlobus User: ", local_user
    print "\tLocal Host: ", local_host
    print "\tLocal Share1: " + local_user + local_share1 + "; Host Endpoint: " + local_folder + " on " + local_user + "#" + local_host
    print "\tLocal Share1 is used to upload data to a remote server"
    print "\tLocal Share2: " + local_user + local_share2 + "; Host Endpoint: " + remote_folder + " on " + remote_user + "#" + remote_host
    print "\tLocal Share2 is used to share data on the remote server with users"
    print "Make sure Globus Server is running with the following configuration: "
    #print "\tGlobus User: ", local_user
    
    path_list = remote_folder.split(os.sep)
    remote_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]
    print "\tRemote Host: ", remote_host
    print "\tRemote Share: " + remote_user + remote_share + "; sharing the remote folder: " + remote_data_share 

def upload(local_directory):
        
    path_list = local_directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep 
    local_date_folder = path_list[len(path_list)-2]

    path_list = remote_folder.split(os.sep)
    remote_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1]

    globus_mkdir = 'mkdir ' +  remote_user + remote_share + ":" + os.sep + remote_data_share + local_date_folder + os.sep        
    globus_scp = "scp -r " + local_user + local_share1 + ":" + os.sep + local_data_share + " " + remote_user + remote_share + ":" + os.sep + remote_data_share + local_date_folder + os.sep 

    if os.path.isdir(local_directory):
        cmd1 = "ssh " + globus_user + globus_address + " " + globus_mkdir
        cmd = "ssh " + globus_user + globus_address + " " + globus_scp + " " + scp_options
        #print "ssh decarlo@cli.globusonline.org scp -r decarlo#data:/txm/ petrel#tomography:dm/"
        print cmd1
        print cmd
        
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
                cmd = "ssh " + globus_user + globus_address + " " + globus_add
                print cmd

    # for demo
    email = 'decarlof@gmail.com'
    globus_add = "acl-add " + local_user + local_share1 + os.sep + local_data_share  + " --perm r --email " + email
    cmd = "ssh " + globus_user + globus_address + " " + globus_add
    #print "ssh decarlo@cli.globusonline.org acl-add decarlo#data/2014-10/g40065r94918/ --perm r --email decarlof@gmail.com"
    print cmd
    #os.system(cmd)
    print "\n\n=================================================================="
    print "Check your email to download the data from globus connect personal"
    print "=================================================================="
      
def share_remote(directory, users):

    path_list = directory.split(os.sep)
    local_data_share = path_list[len(path_list)-2] + os.sep + path_list[len(path_list)-1] + os.sep

    print "\n\tSend a token to share the globus server folder: ", local_data_share
    for tag in users:
        if users[tag].get('email') != None:
            email = str(users[tag]['email'])
            globus_add = "acl-add " + local_user + local_share2 + os.sep + local_data_share  + " --perm r --email " + email
            if validate_email(email) and os.path.isdir(directory):
                cmd = "ssh " + globus_user + globus_address + " " + globus_add
                print cmd

    # for demo
    email = 'decarlof@gmail.com'
    globus_add = "acl-add " + local_user + local_share2 + os.sep + local_data_share  + " --perm r --email " + email
    cmd = "ssh " + globus_user + globus_address + " " + globus_add
    #print "ssh decarlo@cli.globusonline.org acl-add decarlo#data/2014-10/g40065r94918/ --perm r --email decarlof@gmail.com"
    print cmd
    #os.system(cmd)
    print "\n\n=================================================================="
    print "Check your email to download the data from the globus server"
    print "=================================================================="
      
