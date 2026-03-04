=====
Usage
=====

DMagic retrieves user and experiment information from the APS scheduling system. To initialize DMagic status::

    (dm) $ dmagic init
    2024-03-29 20:18:31,165 - General
    2024-03-29 20:18:31,165 -   config           /Users/decarlo/dmagic.conf
    2024-03-29 20:18:31,165 -   verbose          True

this creates the DMagic config file: ~/dmagic.conf with default values.

To configure for your beamline and show the list of users that ran 1,500 days ago from today:

::

    (dm) $ dmagic show --beamline 2-BM-A,B --tomoscan-prefix  2bmb:TomoScan: --set -1500
    2024-03-29 20:20:57,239 - Today's date: 2020-02-19 20:20:57.239632+00:00
    2024-03-29 20:20:57,968 -   Run: 2020-1
    2024-03-29 20:20:57,968 -   PI Name: Weinong Chen
    2024-03-29 20:20:57,969 -   PI affiliation: Purdue University
    2024-03-29 20:20:57,969 -   PI e-mail: wchen@purdue.edu
    2024-03-29 20:20:57,969 -   PI badge: 226531
    2024-03-29 20:20:57,969 -   Proposal GUP: 66310
    2024-03-29 20:20:57,969 -   Proposal Title: In-situ visualization of pull-out behavior of z-pin reinforcement in sandwich panels using X-ray computed tomography
    2024-03-29 20:20:57,969 -   Start date: 2020_02_17
    2024-03-29 20:20:57,969 -   Start time: 2020-02-17 08:00:00-06:00
    2024-03-29 20:20:57,969 -   End Time: 2020-02-19 08:00:00-06:00
    2024-03-29 20:20:57,969 -   User email address:
    2024-03-29 20:20:57,969 -        jonathan.drk@gmail.com
    2024-03-29 20:20:57,969 -        cdkirk@sandia.gov
    2024-03-29 20:20:57,969 -        gzherui@purdue.edu
    2024-03-29 20:20:57,969 -        scpaulson42@gmail.com
    2024-03-29 20:20:57,969 -        nkedir@purdue.edu
    2024-03-29 20:20:57,969 -        wchen@purdue.edu
    2024-03-29 20:20:57,969 -        aleenig@purdue.edu
    2024-03-29 20:20:57,970 - General
    2024-03-29 20:20:57,970 -   config           /Users/decarlo/dmagic.conf
    2024-03-29 20:20:57,970 -   verbose          True
    2024-03-29 20:20:57,970 - Settings
    2024-03-29 20:20:57,970 -   beamline         2-BM-A,B
    2024-03-29 20:20:57,970 -   set              -1500.0
    2024-03-29 20:20:57,970 -   tomoscan_prefix  2bmb:TomoScan:
    2024-03-29 20:20:57,970 -   url              https://beam-api.aps.anl.gov

.. note::
    You only need to pass ``--beamline 2-BM-A,B`` and  ``--tomoscan-prefix 2bmb:TomoScan:`` once,
    then you can only run ``dmagic show``


To update the EPICS PVs with data retrieved from the APS scheduling system run:

::

    (dm) $ dmagic tag
    2024-03-29 20:29:02,028 - Today's date: 2024-03-29 20:29:02.028035
    2024-03-29 20:29:02,700 - User/Experiment PV update
    2024-03-29 20:29:02,701 - Updating pi_name EPICS PV with: Weinong
    2024-03-29 20:29:02,702 - Updating pi_last_name EPICS PV with: Chen
    2024-03-29 20:29:02,703 - Updating pi_affiliation EPICS PV with: Purdue University
    2024-03-29 20:29:02,704 - Updating pi_email EPICS PV with: wchen@purdue.edu
    2024-03-29 20:29:02,705 - Updating pi_badge EPICS PV with: 226531
    2024-03-29 20:29:02,706 - Updating user_info_update_time EPICS PV with: 2024-03-29T20:29:02.028035-05:00
    2024-03-29 20:29:02,707 - Updating proposal_number EPICS PV with: 66310
    2024-03-29 20:29:02,708 - Updating proposal_title EPICS PV with: In-situ visualization of pull-out behavior of z-pin reinforcement in sandwich panels using X-ray computed tomography
    2024-03-29 20:29:02,709 - Updating experiment_date EPICS PV with: 2020-02
    2024-03-29 20:29:02,710 - General
    2024-03-29 20:29:02,710 -   config           /Users/decarlo/dmagic.conf
    2024-03-29 20:29:02,710 -   verbose          True
    2024-03-29 20:29:02,710 - Settings
    2024-03-29 20:29:02,710 -   beamline         2-BM-A,B
    2024-03-29 20:29:02,710 -   set              -1500.0
    2024-03-29 20:29:02,710 -   tomoscan_prefix  2bmb:TomoScan:
    2024-03-29 20:29:02,710 -   url              https://beam-api.aps.anl.gov

The information associated with the current user/experiment will be updated in the medm screen:

.. image:: img/medm_screen.png
  :width: 400
  :alt: medm screen

DM Experiment Management
=========================

The ``create`` and ``email`` commands integrate with the APS Data Management (DM) system
(Sojourner) to manage experiment records and user data access via Globus.

Before using these commands, configure the ``[dm]`` section of ``~/dmagic.conf`` with
your beamline-specific values::

    [dm]
    experiment-type = 7BM
    primary-beamline-contact-badge = 12345
    primary-beamline-contact-email = scientist@anl.gov
    secondary-beamline-contact-badge = 12345
    secondary-beamline-contact-email = scientist@anl.gov
    globus-server-uuid = 054a0877-97ca-4d80-947f-47ca522b173e
    globus-server-top-dir = /gdata/dm/7BM
    globus-message-file = message-7bm.txt

dmagic create
-------------

Creates a DM experiment on Sojourner for the current beamtime and adds all users from
the scheduling proposal. Lists all beamtimes in the current run and prompts for selection::

    (dm) $ dmagic create
    2025-03-04 09:00:00,000 - Found 2 beamtimes in run 2025-1:
      [0] GUP 12345 - PI: Smith - In-situ tomography of ...
           2025-03-03T08:00:00-06:00 to 2025-03-05T08:00:00-06:00
      [1] GUP 67890 - PI: Jones - High-speed imaging of ...
           2025-03-05T08:00:00-06:00 to 2025-03-07T08:00:00-06:00

    Select beamtime [0-1] or 'q' to quit: 0
    2025-03-04 09:00:01,000 - Create summary:
    2025-03-04 09:00:01,000 -    Experiment : 2025-03/2025-03-Smith-12345
    2025-03-04 09:00:01,000 -    Title      : In-situ tomography of ...
       *** Confirm? Yes or No (Y/N): Y
    2025-03-04 09:00:03,000 -    Experiment successfully created: 2025-03-Smith-12345
    2025-03-04 09:00:03,500 -    Added user John Smith to the DM experiment
    2025-03-04 09:00:03,600 -    Added user Jane Doe to the DM experiment

For commissioning runs or staff experiments with no scheduling proposal, use ``--manual``::

    (dm) $ dmagic create --manual --name Staff --title Commissioning --badges 12345,67890

dmagic email
------------

Sends a data-access notification email with a Globus link to all users on the DM
experiment. Requires that ``dmagic create`` has been run first, and that a message
template file (``globus-message-file`` in config) exists::

    (dm) $ dmagic email
    2025-03-04 09:05:00,000 - Sending e-mail to users on the DM experiment
    Send email to users?
       *** Yes or No (Y/N): Y
    2025-03-04 09:05:01,000 -    Would send email to: smith@university.edu, doe@lab.gov, scientist@anl.gov

.. note::
    SMTP sending is currently disabled by default. To enable it, uncomment the
    ``smtplib`` block in ``dmagic/message.py``.

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
        create       Create a DM experiment on Sojourner and add users from the scheduling system
        email        Send data-access email with Globus link to all users on the DM experiment

To access all options::

    (dm) $ dmagic show -h
    usage: dmagic show [-h] [--beamline BEAMLINE] [--set SET] [--tomoscan-prefix TOMOSCAN_PREFIX] [--url URL] [--config FILE] [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --beamline BEAMLINE   beamline name as defined at https://www.aps.anl.gov/Beamlines/Directory, e.g. 2-BM-A,B or 7-BM-B or 32-ID-B,C (default: 7-BM-B)
      --set SET             Number of +/- number days for the current date. Used for setting user info for past/future user groups (default: 0)
      --tomoscan-prefix TOMOSCAN_PREFIX
                            The tomoscan prefix, i.e.'7bmb1:' or '2bma:TomoScan:' (default: 7bmb1:)
      --url URL             URL address of the scheduling system REST API' (default: https://beam-api.aps.anl.gov)
      --config FILE         File name of configuration (default: /Users/decarlo/dmagic.conf)
      --verbose             Verbose output (default: True)

::

    (dm) $ dmagic create -h
    usage: dmagic create [-h] [--beamline BEAMLINE] [--set SET] [--credentials FILE]
                         [--url URL] [--experiment-type TYPE]
                         [--primary-beamline-contact-badge N]
                         [--primary-beamline-contact-email EMAIL]
                         [--secondary-beamline-contact-badge N]
                         [--secondary-beamline-contact-email EMAIL]
                         [--globus-server-uuid UUID] [--globus-server-top-dir DIR]
                         [--globus-message-file FILE]
                         [--manual] [--badges BADGES] [--date DATE]
                         [--name NAME] [--title TITLE] [--config FILE] [--verbose]

    optional arguments:
      --manual              Create a manual experiment (not from the scheduling system)
      --badges BADGES       Comma-separated list of badge numbers for a manual experiment
      --date DATE           Year-month for manual experiment in yyyy-mm format
      --name NAME           PI last name for manual experiment (default: Staff)
      --title TITLE         Title for manual experiment (default: Commissioning)

