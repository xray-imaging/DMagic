=====
Usage
=====

DMagic retrieves user and experiment information from the APS scheduling system and
integrates with the APS Data Management (DM) system (Sojourner) for experiment and
user access management.

Initialization
==============

To create the DMagic configuration file with default values::

    (dm) $ dmagic init

This creates ``~/dmagic.conf``. Edit the ``[site]`` section to configure it for your
beamline before using any other commands::

    [general]

    [settings]
    set = 0

    [site]
    beamline = 2-BM-A,B
    credentials = /home/beams/2BMB/.scheduling_credentials
    experiment-type = 2BM
    globus-message-file = message-2bm.txt
    globus-server-top-dir = /gdata/dm/2BM
    globus-server-uuid = 054a0877-97ca-4d80-947f-47ca522b173e
    primary-beamline-contact-badge = 218262
    primary-beamline-contact-email = pshevchenko@anl.gov
    secondary-beamline-contact-badge = 49734
    secondary-beamline-contact-email = decarlo@anl.gov
    tomoscan-prefix = 2bmb:TomoScan:
    url = https://beam-api.aps.anl.gov
    verbose = True

    [manual]
    name = Staff
    title = Commissioning

    [local]
    analysis = tomodata3
    analysis-top-dir = /data3/2BM/

.. note::
    The ``[site]`` and ``[local]`` sections only need to be configured once per beamline
    installation. The ``[manual]`` section provides defaults for ``dmagic create-manual``.

Scheduling System Commands
==========================

dmagic show
-----------

Queries the APS scheduling REST API to display the currently active experiment::

    (dm) $ dmagic show
    2026-03-04 09:00:00,000 - Today's date: 2026-03-04 09:00:00.000000+00:00
    2026-03-04 09:00:00,700 -   Run: 2026-1
    2026-03-04 09:00:00,701 -   PI Name: Weinong Chen
    2026-03-04 09:00:00,702 -   PI affiliation: Purdue University
    2026-03-04 09:00:00,703 -   PI e-mail: wchen@purdue.edu
    2026-03-04 09:00:00,704 -   PI badge: 226531
    2026-03-04 09:00:00,705 -   Proposal GUP: 66310
    2026-03-04 09:00:00,706 -   Proposal Title: In-situ visualization of ...
    2026-03-04 09:00:00,707 -   Start date: 2026_03_03
    2026-03-04 09:00:00,708 -   Start time: 2026-03-03 08:00:00-06:00
    2026-03-04 09:00:00,709 -   End Time: 2026-03-05 08:00:00-06:00
    2026-03-04 09:00:00,710 -   User email address:
    2026-03-04 09:00:00,711 -        user1@university.edu
    2026-03-04 09:00:00,712 -        user2@lab.gov

Use ``--set N`` to offset the date (negative for past, positive for future)::

    (dm) $ dmagic show --set -1500

dmagic tag
----------

Fetches the same scheduling data and writes it to EPICS PVs on the TomoScan IOC::

    (dm) $ dmagic tag
    2026-03-04 09:00:00,000 - Today's date: 2026-03-04 09:00:00.000000
    2026-03-04 09:00:01,000 - User/Experiment PV update
    2026-03-04 09:00:01,001 - Updating pi_name EPICS PV with: Weinong
    2026-03-04 09:00:01,002 - Updating pi_last_name EPICS PV with: Chen
    2026-03-04 09:00:01,003 - Updating pi_affiliation EPICS PV with: Purdue University
    2026-03-04 09:00:01,004 - Updating pi_email EPICS PV with: wchen@purdue.edu
    2026-03-04 09:00:01,005 - Updating pi_badge EPICS PV with: 226531
    2026-03-04 09:00:01,006 - Updating user_info_update_time EPICS PV with: 2026-03-04T09:00:01-06:00
    2026-03-04 09:00:01,007 - Updating proposal_number EPICS PV with: 66310
    2026-03-04 09:00:01,008 - Updating proposal_title EPICS PV with: In-situ visualization of ...
    2026-03-04 09:00:01,009 - Updating experiment_date EPICS PV with: 2026-03

The information will be updated in the medm screen:

.. image:: img/medm_screen.png
  :width: 400
  :alt: medm screen

DM Experiment Management
=========================

The ``create``, ``create-manual``, ``delete``, ``email``, ``daq-start``, ``daq-stop``,
and ``add-user`` commands integrate with the APS Data Management (DM) system (Sojourner)
to manage experiment records, user data access via Globus, and automated file transfer. These
commands require the ``[site]`` section of ``~/dmagic.conf`` to be correctly configured
(see `Initialization`_ above). The ``daq-start`` and ``daq-stop`` commands additionally
require the ``[local]`` section to be configured with the correct analysis hostname and
data directory.

dmagic create
-------------

Creates a DM experiment on Sojourner for a proposal-based beamtime. Lists all beamtimes
in the current APS run and prompts for selection, then creates the experiment and adds
all users from the scheduling proposal::

    (dm) $ dmagic create
    2026-03-04 09:00:00,000 - Found 3 beamtimes in run 2026-1:
      [ 0] GUP 1018528 - PI: Li - Investigation of multifunctional biomineralized ...
           2026-03-11 to 2026-03-14
      [ 1] GUP 1019623 - PI: Socha - Biomechanical constraints and trade-offs ...
           2026-03-07 to 2026-03-09
      [ 2] GUP 1012039 - PI: Li - Investigation of coupled mechanisms ...
           2026-03-03 to 2026-03-05

    Select beamtime [0-2] or 'q' to quit: 2
    2026-03-04 09:00:05,000 - Create summary:
    2026-03-04 09:00:05,001 -    Experiment : 2026-03/2026-03-Li-1012039
    2026-03-04 09:00:05,002 -    Title      : Investigation of coupled mechanisms ...
       *** Confirm? Yes or No (Y/N): Y
    2026-03-04 09:00:08,000 -    Experiment successfully created: 2026-03-Li-1012039
    2026-03-04 09:00:08,500 -    Added user Tao Li to the DM experiment
    2026-03-04 09:00:08,600 -    Added user Pavel Shevchenko to the DM experiment
    ...
    2026-03-04 09:00:09,000 - ============================================================
    2026-03-04 09:00:09,001 - Experiment name : 2026-03-Li-1012039
    2026-03-04 09:00:09,002 - Globus data link: https://app.globus.org/file-manager?...
    2026-03-04 09:00:09,003 - ============================================================

::

    (dm) $ dmagic create -h
    usage: dmagic create [-h] [--set SET] [--config FILE]

    Create a DM experiment from the APS scheduling system

    options:
      -h, --help     show this help message and exit
      --set SET      Number of +/- days offset from today for past/future user groups (default: 0)
      --config FILE  File name of configuration (default: /home/beams/2BMB/dmagic.conf)

dmagic create-manual
--------------------

Creates a DM experiment manually for commissioning runs or staff experiments that have
no scheduling proposal. Badge numbers, PI name, and title are provided on the command
line::

    (dm) $ dmagic create-manual --name DeCarlo --title "Vibration Tests" --badges 49734,218262

::

    (dm) $ dmagic create-manual -h
    usage: dmagic create-manual [-h] [--badges BADGES] [--date DATE] [--email EMAIL]
                                [--first-name FIRST_NAME] [--institution INSTITUTION]
                                [--name NAME] [--title TITLE] [--config FILE]

    Create a DM experiment manually for commissioning runs

    options:
      -h, --help            show this help message and exit
      --badges BADGES       Comma-separated badge numbers to add to the experiment (default: )
      --date DATE           Year-month in yyyy-mm format (default: current month) (default: )
      --email EMAIL         PI email address (default: )
      --first-name FIRST_NAME
                            PI first name (default: )
      --institution INSTITUTION
                            PI institution (default: )
      --name NAME           PI last name (default: Staff)
      --title TITLE         Experiment title (default: Commissioning)
      --config FILE         File name of configuration (default: /home/beams/2BMB/dmagic.conf)

dmagic delete
-------------

Deletes a DM experiment from Sojourner. Lists all experiments for the configured station
from the last 2 calendar years — this includes both proposal-based and manually created
experiments. Requires double confirmation before deleting::

    (dm) $ dmagic delete
    2026-03-04 22:49:10,028 - Found 11 DM experiment(s) for station 2BM:
      [ 0] 2026-03-Li-1018528                   2026-03-11 to 2026-03-14  Investigation of multifunctional biomineralized ...
      [ 1] 2026-03-Socha-1019623                2026-03-07 to 2026-03-09  Biomechanical constraints and trade-offs ...
      [ 2] 2026-03-Li-1012039                   2026-03-03 to 2026-03-05  Investigation of coupled mechanisms ...
      [ 3] 2026-03-DeCarlo-0                    2026-03-01 to 2026-03-15  Vibration Tests
      [ 4] 2026-03-Staff-0                      2026-03-04 to 2026-03-18  Commissioning
      ...
      [10] Nikitin-2025-06                      2025-06-23 to 2025-06-27  Viktor data from 2025-06

    Select experiment to delete [0-10] or 'q' to quit: 4
    2026-03-04 22:49:39,325 - ============================================================
    2026-03-04 22:49:39,326 - *** PERMANENT DELETION — THIS CANNOT BE UNDONE ***
    2026-03-04 22:49:39,327 -    Experiment     : 2026-03-Staff-0
    2026-03-04 22:49:39,328 -    Storage dir    : /gdata/dm/2BM/2026-03/2026-03-Staff-0
    2026-03-04 22:49:39,329 -    Data dir       : /gdata/dm/2BM/2026-03/2026-03-Staff-0/data
    2026-03-04 22:49:39,330 -    Analysis dir   : /gdata/dm/2BM/2026-03/2026-03-Staff-0/analysis
    2026-03-04 22:49:39,331 - ============================================================
       *** Are you sure? Yes or No (Y/N): Y
       *** Confirm AGAIN to permanently delete all data (Y/N): Y
    2026-03-04 22:49:46,336 - Deleting DM experiment: 2026-03-Staff-0
    2026-03-04 22:49:46,371 -    Experiment 2026-03-Staff-0 successfully deleted

To delete a manually created experiment directly by name (without going through the list)::

    (dm) $ dmagic delete --exp-name 2026-03-Staff-0

::

    (dm) $ dmagic delete -h
    usage: dmagic delete [-h] [--set SET] [--config FILE] [--exp-name EXP_NAME]

    Delete a DM experiment from Sojourner

    options:
      -h, --help           show this help message and exit
      --set SET            Number of +/- days offset from today for past/future user groups (default: 0)
      --config FILE        File name of configuration (default: /home/beams/2BMB/dmagic.conf)
      --exp-name EXP_NAME  [Optional] Full DM experiment name, used only to delete commissioning
                           experiments created with "dmagic create-manual" that are not in the
                           APS scheduling system (e.g. 2026-03-Staff-0). Leave blank to select
                           from the list of all station experiments. (default: None)

dmagic email
------------

Sends a data-access notification email with a Globus link to all users on a DM
experiment. Lists all station experiments and prompts for selection. Requires that
``dmagic create`` or ``dmagic create-manual`` has been run first::

    (dm) $ dmagic email
    2026-03-04 09:05:00,000 - Found 11 DM experiment(s) for station 2BM:
      [ 0] 2026-03-Li-1018528                   2026-03-11 to 2026-03-14  Investigation of ...
      [ 1] 2026-03-Socha-1019623                2026-03-07 to 2026-03-09  Biomechanical ...
      ...

    Select experiment to email [0-10] or 'q' to quit: 0
    2026-03-04 09:05:05,000 - Sending e-mail to users on the DM experiment: 2026-03-Li-1018528
    2026-03-04 09:05:05,100 -    Message to users:
    2026-03-04 09:05:05,200 -    *** All, ...
    Send email to users?
       *** Yes or No (Y/N): Y
    2026-03-04 09:05:06,000 -    Would send email to: user1@university.edu, ..., pshevchenko@anl.gov

::

    (dm) $ dmagic email -h
    usage: dmagic email [-h] [--config FILE]

    Send data-access email with Globus link to all users on the DM experiment

    options:
      -h, --help     show this help message and exit
      --config FILE  File name of configuration (default: /home/beams/2BMB/dmagic.conf)

dmagic daq-start
----------------

Starts automated real-time file transfer (DAQ) to Sojourner. The DM system monitors
the configured directory on the analysis machine for new files and transfers them
continuously. Lists all station experiments and prompts for selection::

    (dm) $ dmagic daq-start
    2026-03-04 09:10:00,000 - Found 11 DM experiment(s) for station 2BM:
      [ 0] 2026-03-Li-1018528                   2026-03-11 to 2026-03-14  Investigation of ...
      [ 1] 2026-03-Li-1012039                   2026-03-03 to 2026-03-05  Investigation of ...
      ...

    Select experiment to start DAQ for [0-10] or 'q' to quit: 1
    2026-03-04 09:10:05,000 - Checking for already running DAQ for experiment 2026-03-Li-1012039
    2026-03-04 09:10:05,100 - Starting DAQ for experiment 2026-03-Li-1012039
    2026-03-04 09:10:05,101 -    Watching directory: @tomodata3:/data3/2BM/2026-03-Li-1012039
    2026-03-04 09:10:06,000 -    DAQ started successfully

The ``analysis`` and ``analysis-top-dir`` settings in ``~/dmagic.conf`` control which
host and directory the DM agent monitors. The monitored path is
``{analysis-top-dir}/{experiment-name}`` on the ``analysis`` host. For best performance,
point ``analysis`` at the storage node (e.g. ``tomodata3``) that physically hosts the
data, rather than a compute node that accesses it via NFS.

::

    (dm) $ dmagic daq-start -h
    usage: dmagic daq-start [-h] [--analysis ANALYSIS] [--analysis-top-dir ANALYSIS_TOP_DIR]
                            [--config FILE]

    Start automated real-time file transfer (DAQ) to Sojourner

    options:
      -h, --help            show this help message and exit
      --analysis ANALYSIS   Hostname of the data analysis computer (default: tomodata3)
      --analysis-top-dir ANALYSIS_TOP_DIR
                            Top-level data directory on the analysis computer (default: /data3/2BM/)
      --config FILE         File name of configuration (default: /home/beams/2BMB/dmagic.conf)

dmagic daq-stop
---------------

Stops all running DAQs for the selected experiment. Lists all station experiments and
prompts for selection::

    (dm) $ dmagic daq-stop
    2026-03-04 18:00:00,000 - Found 11 DM experiment(s) for station 2BM:
      [ 0] 2026-03-Li-1018528                   2026-03-11 to 2026-03-14  Investigation of ...
      [ 1] 2026-03-Li-1012039                   2026-03-03 to 2026-03-05  Investigation of ...
      ...

    Select experiment to stop DAQ for [0-10] or 'q' to quit: 1
    2026-03-04 18:00:05,000 - Stopping all DM DAQs for experiment 2026-03-Li-1012039
    2026-03-04 18:00:05,100 -    Found running DAQ. Stopping now.
    2026-03-04 18:00:06,000 -    Stopped 1 DAQ(s) for experiment 2026-03-Li-1012039

::

    (dm) $ dmagic daq-stop -h
    usage: dmagic daq-stop [-h] [--analysis ANALYSIS] [--analysis-top-dir ANALYSIS_TOP_DIR]
                           [--config FILE]

    Stop all running file transfers for the current experiment

    options:
      -h, --help            show this help message and exit
      --analysis ANALYSIS   Hostname of the data analysis computer (default: tomodata3)
      --analysis-top-dir ANALYSIS_TOP_DIR
                            Top-level data directory on the analysis computer (default: /data3/2BM/)
      --config FILE         File name of configuration (default: /home/beams/2BMB/dmagic.conf)

dmagic add-user
---------------

Adds one or more users to an existing DM experiment by badge number. Lists all station
experiments and prompts for selection, then prompts for badge number(s) if not provided
on the command line::

    (dm) $ dmagic add-user
    2026-03-05 14:32:00,000 - Found 10 DM experiment(s) for station 2BM:
      [ 0] 2026-03-Li-1018528                   2026-03-11 to 2026-03-14  Investigation of ...
      [ 1] 2026-03-Socha-1019623                2026-03-07 to 2026-03-09  Biomechanical ...
      [ 2] 2026-03-Li-1012039                   2026-03-03 to 2026-03-05  Investigation of ...
      ...

    Select experiment to add users to [0-9] or 'q' to quit: 2
    Enter badge number(s) to add (comma-separated): 12345,67890
    2026-03-05 14:32:10,000 -    Added user Jane Smith to the DM experiment
    2026-03-05 14:32:10,100 -    Added user John Doe to the DM experiment

Badge numbers can also be passed directly on the command line::

    (dm) $ dmagic add-user --badges 12345,67890

::

    (dm) $ dmagic add-user -h
    usage: dmagic add-user [-h] [--set SET] [--config FILE] [--badges BADGES]

    Add users to an existing DM experiment by badge number

    options:
      -h, --help       show this help message and exit
      --set SET        Number of +/- days offset from today for past/future user groups (default: 0)
      --config FILE    File name of configuration (default: /home/beams/2BMB/dmagic.conf)
      --badges BADGES  Comma-separated badge number(s) to add to the experiment (e.g. 12345 or 12345,67890) (default: )

Command Reference
=================

::

    (dm) $ dmagic -h
    usage: dmagic [-h] [--config FILE]  ...

    options:
      -h, --help     show this help message and exit
      --config FILE  File name of configuration

    Commands:

        init         Create configuration file
        show         Show user and experiment info from the APS schedule
        tag          Update user info EPICS PVs with info from the APS schedule
        create       Create a DM experiment from the APS scheduling system
        create-manual
                     Create a DM experiment manually for commissioning runs
        delete       Delete a DM experiment from Sojourner
        email        Send data-access email with Globus link to all users on the DM experiment
        daq-start    Start automated real-time file transfer (DAQ) to Sojourner
        daq-stop     Stop all running file transfers for the current experiment
        add-user     Add users to an existing DM experiment by badge number
