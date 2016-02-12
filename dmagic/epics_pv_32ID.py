# -*- coding: utf-8 -*-
"""
Transmission X-ray Microscope process variables grouped by component

"""

from epics import PV

# User Information

pi_name = PV('32idc01:userStringCalc1.AA')
pi_institution = PV('32idc01:userStringCalc1.BB')
pi_badge = PV('32idc01:userStringCalc1.CC')
pi_email = PV('32idc01:userStringCalc1.DD')

proposal_id = PV('32idc01:userStringCalc1.EE')
proposal_title = PV('32idc01:userStringCalc1.FF')
