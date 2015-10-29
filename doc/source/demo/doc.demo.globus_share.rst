Globus Share
============

Module to share a folder with a user by sending an e-mail.

For help and to run::

    python globus_share.py -h

Pre-requisites
++++++++++++++

globus_share relies on the following configuration:

- **personal**: this is a computer where the data you want to share are located. On personal you need to run a Globus connect personal endpoint and configure a Globus shared folder by setting the GMagic `Globus configuration <https://github.com/decarlof/DMagic/blob/master/config/globus.ini>`__.

- Globus_share runs on personal. 


Tasks
+++++

- Data Sharing

    globus_share sends an invitation e-mail (drop-dox style) to the user. Since what is shared is a link to the folder, users will have access to the current and any future content. 


Download file: :download:`globus_share.py<../../../doc/demo/globus_share.py>`

.. literalinclude:: ../../../doc/demo/globus_share.py    :tab-width: 4    :linenos:    :language: guess
