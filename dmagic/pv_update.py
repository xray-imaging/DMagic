#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright (c) 2015-2016, UChicago Argonne, LLC. All rights reserved.    #
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
Module generating user and proposal info PVs
"""
import pytz
from epics import PV
import getpass

from dmagic import scheduling
from dmagic import log

__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2015-2016, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'


def init_PVs(args):
    
    user_pvs = {}
    tomoscan_prefix = args.tomoscan_prefix
    user_pvs['user_name'] = PV(tomoscan_prefix + 'UserName')
    user_pvs['user_last_name'] = PV(tomoscan_prefix + 'UserLastName')
    user_pvs['user_affiliation'] = PV(tomoscan_prefix + 'UserInstitution')
    user_pvs['user_badge'] = PV(tomoscan_prefix + 'UserBadge')
    user_pvs['user_email'] = PV(tomoscan_prefix + 'UserEmail')
    user_pvs['proposal_number'] = PV(tomoscan_prefix + 'ProposalNumber')
    user_pvs['proposal_title'] = PV(tomoscan_prefix + 'ProposalTitle')
    user_pvs['user_info_update_time'] = PV(tomoscan_prefix + 'UserInfoUpdate')
    user_pvs['experiment_date'] = PV(tomoscan_prefix + 'ExperimentYearMonth')
    return user_pvs


def get_credentials(args):
    '''Get the username and password from the user.
    Inputs:
    args: dictionary of configuration parameters
    Returns:
    args with username and password added.
    '''
    clear_credentials = False
    if len(args.username) == 0 or len(args.password) == 0:
        clear_credentials = True
    while len(args.username) == 0:
        try:
            args.username = str(int(input("Enter badge number: ")))
        except:
            log.error('Incorrect username entered.')
            args.username = ''
            continue
    if args.password == '':
        args.password = getpass.getpass()
    return args, clear_credentials


def erase_credentials(args, clear_credentials):
    '''Deletes entries for username and password from input args.
    '''
    if clear_credentials:
        args.username = ''
        args.password = ''
    return args


def pv_daemon(args, date=None):
    user_pvs = init_PVs(args)
    args, clear_credentials = get_credentials(args)
    # set iso format time
    central = pytz.timezone('US/Central')
    local_time = central.localize(date)
    local_time_iso = local_time.isoformat()

    user_pvs['user_info_update_time'].put(local_time_iso)
    log.info("User/Experiment PV update")

    # get PI information
    pi = scheduling.find_pi_info(args, date)
    user_pvs['user_name'].put(pi['name'])
    user_pvs['user_last_name'].put(pi['last_name'])    
    user_pvs['user_affiliation'].put(pi['institution'])
    user_pvs['user_email'].put(pi['email'])
    user_pvs['user_badge'].put(pi['badge'])
    
    # get experiment information
    experiment = scheduling.find_experiment_info(args, date)
    user_pvs['proposal_number'].put(experiment['id'])
    user_pvs['proposal_title'].put(experiment['title'])
    user_pvs['experiment_date'].put(experiment['start'])
    args = erase_credentials(args, clear_credentials)
