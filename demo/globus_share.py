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
Module to share a Globus Personal shared folder with a user by sending an e-mail.
"""

import os
import sys, getopt

import dmagic.globus as gb

__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

def main(argv):
    input_folder = ''
    input_email = ''
    input_mode = 'local'

    try:
        opts, args = getopt.getopt(argv,"hf:e:m:",["ffolder=","eemail=","mmode="])
    except getopt.GetoptError:
        print 'globus_share.py -f <folder> -e <email> -m <mode>'
        print '<folder>: folder path under the globus share'
        print '<email>: e-mail address to send a web link to the shared folder ' 
        print '<mode>: local (default) or remote'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'python globus_share.py -f <folder> -e <email> -m <mode>'
            print "python globus_share.py -f test -e decarlof@gmail.com -m remote"
            print '\t<folder>:folder path under the globus share'
            print '\t<email>:e-mail address to send a link to the shared folder ' 
            print '\t<mode>:local (default) or remote\n'
            sys.exit()
        elif opt in ("-f", "--ffolder"):
            input_folder = arg
        elif opt in ("-e", "--eemail"):
            input_email = arg
        elif opt in ("-m", "--mmode"):
            input_mode = arg

    input_folder = os.path.normpath(input_folder) + os.sep # will add the trailing slash if it's not already there.
            
    cmd = gb.share(input_folder, input_email, input_mode)
    print cmd

    if cmd == -1: 
        print "ERROR: email is not valid ..."
        print "EXAMPLE: python globus_share.py -f test -e decarlof@gmail.com -m remote"
        print input_folder, "does not exists under the Globus Personal Share folder"
        gb.dm_settings()    
        
    elif cmd == -2: 
        print "ERROR: " + input_folder + " does not exists under the Globus Personal Share folder"
        print "EXAMPLE: python globus_share.py -f test -e decarlof@gmail.com -m remote"
        gb.dm_settings()    
    else:
        #os.system(cmd)
        print "Download link sent to: ", input_email

if __name__ == "__main__":
    main(sys.argv[1:])

