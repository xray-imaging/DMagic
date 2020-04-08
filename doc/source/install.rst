=======
Install
=======

This section covers the basics of how to download and install `DMagic <https://github.com/xray-imaging/DMagic>`_.

.. contents:: Contents:
   :local:


Pre-requisites
==============


Install from `Anaconda <https://www.anaconda.com/distribution/>`_ python3.x.

Before using `DMagic <https://github.com/xray-imaging/DMagic>`_  you need to have valid APS credentials
to access the `APS scheduling system <https://schedule.aps.anl.gov/>`__.


Installing from source
======================

In a prepared virtualenv or as root for system-wide installation clone the `DMagic <https://github.com/xray-imaging/DMagic>`_
from `GitHub <https://github.com>`_ repository

::

    $ git clone https://github.com/xray-imaging/DMagic DMagic

Edit the config.py file::

    $ gedit DMagic/dmagic/config.py

by entering the correct values for::

    USERNAME = '123456'
    PASSWORD = 'password'
    BEAMLINE = "2-BM-A,B"

then::

    $ cd DMagic
    $ python setup.py install

.. warning:: If your python installation is in a location different from #!/usr/bin/env python please edit the first line of the bin/dmagic file to match yours.

EPICS tools
===========


* Copy and customize in your EPICS ioc boot directory the :download:`experimentInfo.db <../demo/epics/experimentInfo.db>` and :download:`experimentInfo_settings.req <../demo/epics/experimentInfo_settings.req>` files.

* Edit your EPICS ioc start up script by adding:

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

    $ pip install suds-py3 
    $ pip install ipdb
    $ pip install validate-email
    $ pip install pyinotify
    $ pip install pyepics


.. warning:: If requiere edit your .cshrc to set PYEPICS_LIBCA: Example: setenv PYEPICS_LIBCA /APSshare/epics/extensions-base/3.14.12.2-ext1/lib/linux-x86_64/libca.so


