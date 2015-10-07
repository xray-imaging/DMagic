# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 16:38:41 2015

@author: decarlo
"""
import pytz
import datetime
import ConfigParser

import scheduling as sch
import globus as gb

cf = ConfigParser.ConfigParser()
cf.read('credentials.ini')
beamline = cf.get('settings', 'beamline')

gb.settings()

now = datetime.datetime(2014, 10, 18, 10, 10, 30).replace(tzinfo=pytz.timezone('US/Central'))
print "\n\nExperiment date: ", now

exp_start = sch.find_experiment_start(beamline, now)
print "Experiment starting date/time: ", exp_start

exp_id = sch.create_experiment_id(beamline, now)
print "Unique experiment ID: ", exp_id
                  
unique_directory = gb.create_unique_directory(exp_start, exp_id)
users = sch.find_users(beamline, now)

#sch.print_users(users)
#gb.local_share(unique_directory, users)

gb.upload(unique_directory, users)

