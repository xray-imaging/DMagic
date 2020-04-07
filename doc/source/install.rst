==================
Install directions
==================

This section covers the basics of how to download and install `DMagic <https://github.com/decarlof/DMagic>`_.

.. contents:: Contents:
   :local:


Pre-requisites
==============


Install from `Anaconda <https://www.anaconda.com/distribution/>`_ python3.x.

Before using `DMagic <https://github.com/xray-imaging/DMagic>`_  you need to have valid APS credentials
to access the `APS scheduling system <https://schedule.aps.anl.gov/>`__.


Installing from source
======================

Install the following::

    pip install suds-py3 
    pip install ipdb
    pip install validate-email
    pip install pyinotify
    
Clone the `DMagic <https://github.com/decarlof/DMagic>`_  
from `GitHub <https://github.com>`_ repository::

    git clone https://github.com/xray-imaging/DMagic DMagic

then::

    cd DMagic
    python setup.py install

