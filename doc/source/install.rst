==================
Install directions
==================

This section covers the basics of how to download and install data-management.

.. contents:: Contents:
   :local:

Pre-requisites
==============

Before using the Data Management toolbox  you need to have setup an account 
on `Globus <https://www.globus.org/>`__ and installed a 
`Globus Connect Personal endpoint <https://www.globus.org/globus-connect-personal/>`__
on the APS computer you want to share data from. You also need valid 
APS credentials to access the `APS scheduling system <https://schedule.aps.anl.gov/>`__.
You must also create in your home directory configuration files for 
`globus <https://github.com/decarlof/data-management/blob/master/config/globus.ini>`__ 
and `scheduling <https://github.com/decarlof/data-management/blob/master/config/credentials.ini>`__ 
systems.

Being a beta tester
===================

Data Management has been installed at 2-BM and 32-ID as a beta version. If you would like 
to be a beta tester please clone the `data-management repository <https://github.com/decarlof/data-management>`__ 
from `GitHub <https://github.com>`_.

The beta version includes the following funtionalities:

    For a given experiment date retrieves the uses' email addresses from the APS scheduling system.
    Automatically send an e-mail to the users with a link (drop-box style) to retrieve the data.
    Data can be shared directly from the beamline machine or, after a globus copy, from petrel.

To contribute back to the project please follow the `development <http://img-data-management.readthedocs.org/en/latest/source/devguide.html>`_
instructions.
 
Installing from Conda/Binstar
=============================

First you must have `Conda <http://continuum.io/downloads>`_ 
installed, then open a terminal or a command prompt window and run::

    conda install -c https://conda.anaconda.org/decarlof data-management


Updating the installation
=========================

Data Management is an active project, so we suggest you update your installation 
frequently. To update the installation run in your terminal::

    conda update -c https://conda.anaconda.org/decarlof data-management

For some more information about using Conda, please refer to the 
`docs <http://conda.pydata.org/docs>`__.
    
