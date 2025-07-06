=====
Usage
=====

DMagic retrieves user and experiment information from the APS scheduling system. To initlialize DMagic status::

    (dm) $ dmagic init
    2024-03-29 20:18:31,165 - General
    2024-03-29 20:18:31,165 -   config           /Users/decarlo/dmagic.conf
    2024-03-29 20:18:31,165 -   verbose          True

this creates the DMagic config file: ~/dmagic.conf with default values.

To configure for your beamline and show the list of users that run 1,500 days ago from today:

::

    (dm) $ dmagic show --beamline 2-BM-A,B --tomoscan-prefix  2bmb:TomoScan: --set -1500
    2024-03-29 20:20:57,239 - Today's date: 2020-02-19 20:20:57.239632
    2024-03-29 20:20:57,968 -   Run: 2020-1
    2024-03-29 20:20:57,968 -   PI Name: Weinong Chen
    2024-03-29 20:20:57,969 -   PI affiliation: Purdue University
    2024-03-29 20:20:57,969 -   PI e-mail: wchen@purdue.edu
    2024-03-29 20:20:57,969 -   PI badge: 226531
    2024-03-29 20:20:57,969 -   Proposal GUP: 66310
    2024-03-29 20:20:57,969 -   Proposal Title: In-situ visualization of pull-out behavior of z-pin reinforcement in sandwich panels using X-ray computed tomography
    2024-03-29 20:20:57,969 -   Start time: s
    2024-03-29 20:20:57,969 -   End Time: s
    2024-03-29 20:20:57,969 -   User email address: 
    2024-03-29 20:20:57,969 -       jonathan.drk@gmail.com
    2024-03-29 20:20:57,969 -       cdkirk@sandia.gov
    2024-03-29 20:20:57,969 -       gzherui@purdue.edu
    2024-03-29 20:20:57,969 -       scpaulson42@gmail.com
    2024-03-29 20:20:57,969 -       nkedir@purdue.edu
    2024-03-29 20:20:57,969 -       wchen@purdue.edu
    2024-03-29 20:20:57,969 -       aleenig@purdue.edu
    2024-03-29 20:20:57,969 -       wchen@purdue.edu
    2024-03-29 20:20:57,970 - General
    2024-03-29 20:20:57,970 -   config           /Users/decarlo/dmagic.conf
    2024-03-29 20:20:57,970 -   verbose          True
    2024-03-29 20:20:57,970 - Settings
    2024-03-29 20:20:57,970 -   beamline         2-BM-A,B
    2024-03-29 20:20:57,970 -   set              -1500.0
    2024-03-29 20:20:57,970 -   tomoscan_prefix  2bmb:TomoScan:
    2024-03-29 20:20:57,970 -   url              https://mis7.aps.anl.gov:7004

.. note::
    You only need to pass ``--beamline 2-BM-A,B`` and  ``--tomoscan-prefix 2bmb:TomoScan:`` once, 
    then you can only run ``dmagic show``


To update the EPICS PVs with data retrieved from the APS scheduling system run:

::

    (dm) $ dmagic tag
    2024-03-29 20:29:02,028 - Today's date: 2024-03-29 20:29:02.028035
    2024-03-29 20:29:02,700 - User/Experiment PV update
    2024-03-29 20:29:04,701 - Updated EPICS PV with: Weinong
    2024-03-29 20:29:06,701 - Updated EPICS PV with: Chen
    2024-03-29 20:29:08,702 - Updated EPICS PV with: Purdue University
    2024-03-29 20:29:10,702 - Updated EPICS PV with: wchen@purdue.edu
    2024-03-29 20:29:12,702 - Updated EPICS PV with: 226531
    2024-03-29 20:29:14,704 - Updated EPICS PV with: 2024-03-29T20:29:02.028035-05:00
    2024-03-29 20:29:16,704 - Updated EPICS PV with: 66310
    2024-03-29 20:29:18,704 - Updated EPICS PV with: In-situ visualization of pull-out behavior of z-pin reinforcement in sandwich panels using X-ray computed tomography
    2024-03-29 20:29:20,707 - Updated EPICS PV with: 2020-02
    2024-03-29 20:29:20,707 - General
    2024-03-29 20:29:20,707 -   config           /Users/decarlo/dmagic.conf
    2024-03-29 20:29:20,707 -   verbose          True
    2024-03-29 20:29:20,707 - Settings
    2024-03-29 20:29:20,707 -   beamline         2-BM-A,B
    2024-03-29 20:29:20,707 -   set              -1500.0
    2024-03-29 20:29:20,707 -   tomoscan_prefix  2bmb:TomoScan:
    2024-03-29 20:29:20,707 -   url              https://mis7.aps.anl.gov:7004

The information associated with the current user/experiment will be updated in the medm screen: 

.. image:: img/medm_screen.png
  :width: 400
  :alt: medm screen

For help::

    (dm) $ dmagic -h
    usage: dmagic [-h] [--config FILE]  ...

    optional arguments:
      -h, --help     show this help message and exit
      --config FILE  File name of configuration

    Commands:
      
        init         Create configuration file
        show         Show user and experiment info from the APS schedule
        tag          Update user info EPICS PVs with info from the APS schedule

To access all options::

    (dm) $ dmagic show -h
    usage: dmagic [-h] [--config FILE]  ...

    optional arguments:
      -h, --help     show this help message and exit
      --config FILE  File name of configuration

    Commands:
      
        init         Create configuration file
        show         Show user and experiment info from the APS schedule
        tag          Update user info EPICS PVs with info from the APS schedule
    (dm) decarlo@marmot DMagic-decarlof % dmagic show -h
    usage: dmagic show [-h] [--beamline BEAMLINE] [--set SET] [--tomoscan-prefix TOMOSCAN_PREFIX] [--url URL] [--config FILE] [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --beamline BEAMLINE   beamline name as defined at https://www.aps.anl.gov/Beamlines/Directory, e.g. 2-BM-A,B or 7-BM-B or 32-ID-B,C (default: 7-BM-B)
      --set SET             Number of +/- number days for the current date. Used for setting user info for past/future user groups (default: 0)
      --tomoscan-prefix TOMOSCAN_PREFIX
                            The tomoscan prefix, i.e.'7bmb1:' or '2bma:TomoScan:' (default: 7bmb1:)
      --url URL             URL address of the scheduling system REST API' (default: https://mis7.aps.anl.gov:7004)
      --config FILE         File name of configuration (default: /Users/decarlo/dmagic.conf)
      --verbose             Verbose output (default: True)

::

    (dm) $ dmagic tag -h
    usage: dmagic tag [-h] [--beamline BEAMLINE] [--set SET] [--tomoscan-prefix TOMOSCAN_PREFIX] [--url URL] [--config FILE] [--verbose]
    
    optional arguments:
      -h, --help            show this help message and exit
      --beamline BEAMLINE   beamline name as defined at https://www.aps.anl.gov/Beamlines/Directory, e.g. 2-BM-A,B or 7-BM-B or 32-ID-B,C (default: 7-BM-B)
      --set SET             Number of +/- number days for the current date. Used for setting user info for past/future user groups (default: 0)
      --tomoscan-prefix TOMOSCAN_PREFIX
                            The tomoscan prefix, i.e.'7bmb1:' or '2bma:TomoScan:' (default: 7bmb1:)
      --url URL             URL address of the scheduling system REST API' (default: https://mis7.aps.anl.gov:7004)
      --config FILE         File name of configuration (default: /Users/decarlo/dmagic.conf)
      --verbose             Verbose output (default: True)

