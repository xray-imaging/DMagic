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

Installing from Conda/Binstar
=============================

First you must have `Conda <http://continuum.io/downloads>`_ 
installed, then open a terminal or a command prompt window and run::

    conda install -c decarlof data_management


Updating the installation
=========================

TomoPy is an active project, so we suggest you update your installation 
frequently. To update the installation run in your terminal::

    conda update -c decarlof data_management

For some more information about using Conda, please refer to the 
`docs <http://conda.pydata.org/docs>`__.
    
