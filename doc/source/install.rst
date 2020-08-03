=======
Install
=======

This section covers the basics of how to download and install `DMagic <https://github.com/xray-imaging/DMagic>`_.

.. contents:: Contents:
   :local:


Pre-requisites
==============


Install from `Anaconda <https://www.anaconda.com/distribution/>`_ python3.x.

You will also need to have the APS Data Management system installed for your beamline; contact 
the SDM group for this installation.  You will need to download the Data Management API via conda

::

    conda install -c aps-anl-tag aps-dm-api

There are also several environment variables that must be set for the DM API to work properly.  They can be found in the /home/dm_bm/etc/dm.conda.setup.sh script.  Copy everything in this script except the change to the PATH to your account's ~/.bashrc file.


Installing from source
======================

In a prepared virtualenv or as root for system-wide installation clone the `DMagic <https://github.com/xray-imaging/DMagic>`_
from `GitHub <https://github.com>`_ repository

::

    $ git clone https://github.com/xray-imaging/DMagic DMagic

Edit the config.py file with the name of your beamline, the IOC prefix for the experiment info PVs for your beamline, and any portions of the EPICS name between this IOC prefix and the actual PV names::

    $ gedit DMagic/dmagic/config.py

To install DMagic, run::

    $ cd DMagic
    $ python setup.py install

.. warning:: If your python installation is in a location different from #!/usr/bin/env python please edit the first line of the bin/dmagic file to match yours.


EPICS tools
===========


* Copy and customize in your EPICS ioc boot directory the :download:`experimentInfo.db <../demo/epics/experimentInfo.db>` and :download:`experimentInfo_settings.req <../demo/epics/experimentInfo_settings.req>` files.

* Edit your EPICS ioc start up script by adding (as an example for an IOC named 32idcTXM):

::

    dbLoadRecords("$(TOP)/experimentInfo.db", "P=32idcTXM:")

* Add a link to your main MEDM screen to load the :download:`experiment_info.adl <../demo/epics/experiment_info.adl>`

.. image:: img/medm_screen.png
  :width: 400
  :alt: medm screen

* Customize the dmagic/pv_beamline.py file to match the PV names in use at your beamline (see examples for 2-BM :download:`pv_beamline_2bm.py <../demo/epics/pv_beamline_2bm.py>` and 7-BM :download:`pv_beamline_7bm.py <../demo/epics/pv_beamline_2bm.py>`


Update
======

**dmagic** is constantly updated to include new features. To update your locally installed version::

    $ cd dmagic
    $ git pull
    $ python setup.py install


Dependencies
============

Install the following package::

    $ pip install validate-email
    $ pip install pyinotify
    $ pip install pyepics


.. warning:: If requiere edit your .cshrc to set PYEPICS_LIBCA: Example: setenv PYEPICS_LIBCA /APSshare/epics/extensions-base/3.14.12.2-ext1/lib/linux-x86_64/libca.so


