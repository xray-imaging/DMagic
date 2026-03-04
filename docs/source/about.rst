=====
About
=====

`DMagic <https://github.com/xray-imaging/DMagic>`_ provides a command-line interface to the
`APS scheduling system <https://schedule.aps.anl.gov/>`_.

It bridges the APS scheduling system (which tracks who is running experiments and when) with
the `EPICS <https://epics-controls.org/>`_ control system used to operate beamline equipment.

For the current experiment, DMagic can retrieve PI and user information (name, affiliation,
email, badge number) as well as proposal metadata (GUP ID, title, start/end times). This
information can be printed to the terminal (``show`` command) or written directly into EPICS
Process Variables on the beamline IOC (``tag`` command), ensuring that data files are
automatically attributed to the correct user group without manual entry.

DMagic is primarily used at tomography beamlines (e.g. 2-BM, 7-BM, 32-ID) in conjunction
with `tomoScan <https://tomoscan.readthedocs.io/>`_ to populate user information PVs at the
start of each user run.
