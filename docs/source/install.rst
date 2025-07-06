=======
Install
=======

This section covers the basics of how to download and install `DMagic <https://github.com/xray-imaging/DMagic>`_.

.. contents:: Contents:
   :local:

Installing from source
======================

Install from `Anaconda <https://www.anaconda.com/distribution/>`_ > python3.9

Create and activate a dedicated conda environment::

    (base) $ conda create --name dm python=3.11
    (base) $ conda activate dm
    (dm) $ 

Clone the  `DMagic <https://github.com/xray-imaging/DMagic>`_ repository

::

    (dm) $ git clone https://github.com/xray-imaging/DMagic DMagic

Install DMagic::

    (dm) $ cd DMagic
    (dm) $ pip install .

Install all packages listed in the ``env/requirements.txt`` file::

    (dm) $ conda install pytz
    (dm) $ conda install requests
    (dm) $ pip install pyepics

Test the installation
=====================

Before using DMagic you must create a file with default name .scheduling_credentials in the user 
home directory containing: username|pwd to access the restAPI service.


::

    (dm) $ dmagic -h
    usage: dmagic [-h] [--config FILE]  ...

    optional arguments:
      -h, --help     show this help message and exit
      --config FILE  File name of configuration

    Commands:
      
        init         Create configuration file
        show         Show user and experiment info from the APS schedule
        tag          Update user info EPICS PVs with info from the APS schedule


Configuration
=============

To run DMagic you need to set the beamline name as defined in the `APS scheduling system <https://www.aps.anl.gov/Beamlines/Directory>`_, and the user info PVs where to store the information retrieved from the scheduling system.  If you are using `tomoScan <https://tomoscan.readthedocs.io/en/latest/>`_ these are provided in the 
beamline specific section `user information <https://tomoscan.readthedocs.io/en/latest/tomoScanApp.html#user-information>`_ section. 

Once you have this information you can update the DMagic configuration i.e. the name of your beamline and the 
IOC prefix where the PVs are stored at runtime using the --beamline and --tomoscan-prefix options. For more info::

    (dm) $ dmagic show -h
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

If you are not running `tomoScan <https://tomoscan.readthedocs.io/en/latest/>`_ look at the EPICS tools section below.


EPICS tools
===========

If you are not running `tomoScan <https://tomoscan.readthedocs.io/en/latest/>`_:

* Copy and customize in your EPICS ioc boot directory the :download:`experimentInfo.db <../demo/epics/experimentInfo.db>` and :download:`experimentInfo_settings.req <../demo/epics/experimentInfo_settings.req>` files.

* Edit your EPICS ioc start up script by adding (as an example for an IOC named 32idcTXM):

::

    dbLoadRecords("$(TOP)/experimentInfo.db", "P=32idcTXM:")

* Add a link to your main MEDM screen to load the :download:`experiment_info.adl <../demo/epics/experiment_info.adl>`

.. image:: img/medm_screen.png
  :width: 400
  :alt: medm screen


Update
======

**dmagic** is constantly updated to include new features. To update your locally installed version::

    (dm) $ cd dmagic
    (dm) $ git pull
    (dm) $ pip install .


Dependencies
============

Install the following package::

    $ pip install pyepics
    $ pip install pytz
    $ conda install decorator
    $ conda install numpy

.. warning:: If required edit your .cshrc or .bashrc to set PYEPICS_LIBCA: Example: setenv PYEPICS_LIBCA /APSshare/epics/extensions-base/3.14.12.2-ext1/lib/linux-x86_64/libca.so


