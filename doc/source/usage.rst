=====
Usage
=====

Initlialize DMagic status::

    $ dmagic init

this creates the DMagic config file: ~/dmagic.conf.

::

    $ dmagic show

To update the EPICS PVs with data retrieved from the APS scheduling system run:

::

    $ dmagic tag

The information associated with the current user/experiment will be updated in the medm screen: 

.. image:: img/medm_screen.png
  :width: 400
  :alt: medm screen

For help and to access all options::

    dmagic -h
    dmagic show -h
    dmagic tag -h




