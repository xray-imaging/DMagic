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
import datetime
import pytz
from epics import PV

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


def update(args, date=None):

    auth      = scheduling.authorize()
    run       = scheduling.current_run(auth, args)
    proposals = scheduling.beamtime_requests(run, auth, args)

    if not proposals:
        log.error('No valid current experiment')
        return None
    try:
        log.error(proposals['message'])
        return None
    except:
        pass

    proposal = scheduling.get_current_proposal(proposals, args)
    if not proposal:
        log.warning('No valid current proposal')
        return

    # get PI information
    pi = scheduling.get_current_pi(proposal)

    user_pvs = init_PVs(args)

    log.info("User/Experiment PV update")
    user_pvs['user_name'].put(pi['firstName'])
    log.info('Updated EPICS PV with: %s' % pi['firstName'])
    user_pvs['user_last_name'].put(pi['lastName'])    
    log.info('Updated EPICS PV with: %s' % pi['lastName'])    
    user_pvs['user_affiliation'].put(pi['institution'])
    log.info('Updated EPICS PV with: %s' % pi['institution'])
    user_pvs['user_email'].put(pi['email'])
    log.info('Updated EPICS PV with: %s' % pi['email'])
    user_pvs['user_badge'].put(pi['badge'])
    log.info('Updated EPICS PV with: %s' % pi['badge'])

    # set iso format time
    central = pytz.timezone('US/Central')
    local_time = central.localize(date)
    local_time_iso = local_time.isoformat()
    user_pvs['user_info_update_time'].put(local_time_iso)
    log.info('Updated EPICS PV with: %s' % local_time_iso)
    
    # get experiment information
    user_pvs['proposal_number'].put(scheduling.get_current_proposal_id(proposal))
    log.info('Updated EPICS PV with: %s' % scheduling.get_current_proposal_id(proposal))
    user_pvs['proposal_title'].put(scheduling.get_current_proposal_title(proposal))
    log.info('Updated EPICS PV with: %s' % scheduling.get_current_proposal_title(proposal))
    #Make the start date of the experiment into a year - month
    start_datetime = datetime.datetime.strptime(scheduling.fix_iso(proposal['startTime']),'%Y-%m-%dT%H:%M:%S%z')
    user_pvs['experiment_date'].put(start_datetime.strftime('%Y-%m'))
    log.info('Updated EPICS PV with: %s' % start_datetime.strftime('%Y-%m'))
