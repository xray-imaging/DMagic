=======
Install
=======

This section covers how to install `DMagic <https://github.com/xray-imaging/DMagic>`_ on a new beamline account.

.. contents:: Contents:
   :local:

Install
=======

Requires `Anaconda <https://www.anaconda.com/distribution/>`_ with Python 3.9 or later.

Create and activate a conda environment::

    (base) $ conda create --name dm python=3.11
    (base) $ conda activate dm

Clone and install DMagic::

    (dm) $ git clone https://github.com/xray-imaging/DMagic DMagic
    (dm) $ cd DMagic
    (dm) $ pip install .
    (dm) $ pip install pytz pyyaml requests pyepics

Install the APS Data Management SDK::

    (dm) $ conda install apsu::aps-dm-api

.. note::
    The DM SDK is required for ``create``, ``delete``, ``email``, ``add-user``,
    ``remove-user``, ``daq-start``, and ``daq-stop``. Without it, ``dmagic show``
    and ``dmagic tag`` still work and dmagic will print a warning for the other commands.


Configure
=========

Credentials
-----------

Create a credentials file for the APS scheduling REST API::

    $ echo "username|password" > ~/.scheduling_credentials
    $ chmod 600 ~/.scheduling_credentials

Replace ``username`` and ``password`` with your APS beamline scheduling credentials.

DM environment variables
------------------------

The DM SDK requires environment variables to locate the DM web services. These are
beamline-specific. Look up the values for your beamline in
``/home/dm_id/etc/dm.setup.sh`` on any machine where the DM system is configured,
then add them to ``~/.bashrc``::

    export DM_ROOT_DIR=/home/dm_id/production
    export DM_DS_WEB_SERVICE_URL=https://<ds-host>:<port>
    export DM_DAQ_WEB_SERVICE_URL=https://<daq-host>:<port>
    export DM_CAT_WEB_SERVICE_URL=https://<daq-host>:<cat-port>
    export DM_PROC_WEB_SERVICE_URL=https://<daq-host>:<proc-port>
    export DM_APS_DB_WEB_SERVICE_URL=https://<ds-host>:<db-port>
    export DM_STATION_NAME=<STATION>          # e.g. 2BM or 32ID
    export DM_LOGIN_FILE=/home/dm_id/etc/.<login-file>
    export DM_BEAMLINE_NAME=<beamline>        # e.g. 2-BM-A,B or 32-ID-B,C

DMagic configuration file
--------------------------

Run ``dmagic init`` to create ``~/dmagic.conf`` with default values::

    (dm) $ dmagic init

Then edit the ``[site]`` section to match your beamline. The key fields are:

* ``beamline`` — beamline ID as listed in the `APS scheduling system <https://www.aps.anl.gov/Beamlines/Directory>`_, e.g. ``2-BM-A,B`` or ``32-ID-B,C``
* ``credentials`` — path to your ``~/.scheduling_credentials`` file
* ``experiment-type`` — station name used by the DM system, e.g. ``2BM`` or ``32ID``
* ``primary-beamline-contact-badge`` / ``secondary-beamline-contact-badge`` — badge numbers for beamline staff auto-added to every experiment
* ``tomoscan-prefix`` — EPICS IOC prefix used by ``dmagic tag``, e.g. ``2bmb:TomoScan:``

See the `Usage <usage.html>`_ page for a full annotated example.

.. note::
    The ``[site]`` section only needs to be set once. Do not run ``dmagic init``
    again after configuring it — that would overwrite your settings.


Test
====

::

    (dm) $ dmagic show

This should display the currently active proposal for your beamline. If the DM SDK
is also installed and the environment variables are set correctly::

    (dm) $ dmagic create


Update
======

::

    (dm) $ cd DMagic
    (dm) $ git pull
    (dm) $ pip install .
