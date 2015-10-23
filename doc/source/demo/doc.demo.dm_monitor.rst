Experiment Monitor
==================

DMagic active directory monitoring example (Download file: :download:`dm_monitor.py<../../../doc/demo/dm_monitor.py>`)

Pre-requisites
++++++++++++++

Experiment Monitor relies on the following configuration:

- local: this is the computer where the detector is connected. The raw data directory is located on a local disk of this computer. Experiment Monitor runs on local.

- personal: this is a computer, generally different from local, where the data analysis will be completed. On personal you need to run a Globus connect personal endpoint and configure a Globus shared folder by setting the GMagic `Globus configuration <https://github.com/decarlof/DMagic/blob/master/config/globus.ini>`__.


- access to the APS scheduling system by setting the GMagic `Scheduling configuration <https://github.com/decarlof/DMagic/blob/master/config/scheduling.ini>`__.

- ssh public key sharing: local and personal are configured to ssh into each other with no password required.


Tasks
+++++

.. contents:: Contents:
   :local:

- Unique raw data directory creation on local

    Experiment Monitor creates a unique folder as YYYY-MM/pi_last_name on local using the current date and accessing the APS scheduling system.

- Data Collection
    
    Configure your data collection software to store the raw data in the newly created directory at YYYY-MM/pi_last_name and start to collect data.
    
- Data Monitoring
    
    Experiment Monitor will look for new files at YYYY-MM/pi_last_name and copy them to personal under its Globus shared folder.
    
- Data Sharing

    An invitation e-mail is sent to the users to access the Globus personal shared folder. The user e-mails are retrieved using the current date and accessing the APS scheduling system. Since what is shared is a link to the folder, users will have access to the raw data as they are collected and to any data analysis results generated in the same folder at a later time.


