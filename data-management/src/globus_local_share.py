# -*- coding: utf-8 -*-
"""
.. module:: globus_share.py
   :platform: Unix
   :synopsis:   
        Share via Globus a data directory with the users email 
   :INPUT
        folder, email 

.. moduleauthor:: Francesco De Carlo <decarlof@gmail.com>

""" 

import os
import sys, getopt
import ConfigParser
from validate_email import validate_email


# see README.txt to set a globus personal shared folder
cf = ConfigParser.ConfigParser()
cf.read('globus.ini')
globus_address = cf.get('settings', 'cli_address')
globus_user = cf.get('settings', 'cli_user')

local_user = cf.get('globus connect personal', 'user') 
local_share1 = cf.get('globus connect personal', 'share1') 
local_share2 = cf.get('globus connect personal', 'share2') 
local_shared_folder = cf.get('globus connect personal', 'shared_folder')  

remote_user = cf.get('globus remote server', 'user') 
remote_share = cf.get('globus remote server', 'share') 
remote_shared_folder = cf.get('globus remote server', 'shared_folder')  

def main(argv):
    input_folder = ''
    input_email = ''

    try:
        opts, args = getopt.getopt(argv,"hf:e:",["ffolder=","eemail="])
    except getopt.GetoptError:
        print 'test.py -f <folder> -e <email>'
        #print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'globus_share.py -f <folder> -e <email>'
            sys.exit()
        elif opt in ("-f", "--ffolder"):
            input_folder = arg
        elif opt in ("-e", "--eemail"):
            input_email = arg
    
    input_folder = os.path.normpath(input_folder) + os.sep # will add the trailing slash if it's not already there.

    globus_add = "acl-add " + local_user + local_share1 + os.sep + input_folder  + " --perm r --email " + input_email
#    globus_add = "acl-add " + local_user + local_share2  + os.sep + input_folder + " --perm r --email " + input_email

    print "python globus_local_share.py -f test -e decarlof@gmail.com"
    if validate_email(input_email) and os.path.isdir(local_shared_folder + input_folder):
        cmd = "ssh " + globus_user + globus_address + " " + globus_add
        print cmd
        print "ssh decarlo@cli.globusonline.org acl-add decarlo#data/test/ --perm r --email decarlof@gmail.com"
        #os.system(cmd)
        print "Download link sent to: ", input_email
    else:
        print "ERROR: "
        if not validate_email(input_email):
            print "email is not valid ..."
        else:
            print local_shared_folder + input_folder, "does not exists on the local server", 

    
if __name__ == "__main__":
    main(sys.argv[1:])

