=====
About
=====

`DMagic <https://github.com/xray-imaging/DMagic>`_ provides a command-line interface to the
`APS scheduling system <https://schedule.aps.anl.gov/>`_ and the APS Data Management (DM)
system (`Sojourner <https://dm.aps.anl.gov/>`_).

Scheduling System Integration
------------------------------

DMagic bridges the APS scheduling system (which tracks who is running experiments and when)
with the `EPICS <https://epics-controls.org/>`_ control system used to operate beamline
equipment.

For the current experiment, DMagic can retrieve PI and user information (name, affiliation,
email, badge number) as well as proposal metadata (GUP ID, title, start/end times). This
information can be printed to the terminal (``dmagic show``) or written directly into EPICS
Process Variables on the beamline IOC (``dmagic tag``), ensuring that data files are
automatically attributed to the correct user group without manual entry.

DM Experiment Management
-------------------------

DMagic also integrates with the APS Data Management system (Sojourner) to manage experiment
records and user data access via `Globus <https://www.globus.org/>`_.

For each beamtime, ``dmagic create`` registers a new experiment in Sojourner, creates the
data directory structure on the beamline storage system, and grants Globus access to all
users listed in the scheduling proposal. The experiment name follows the format
``{YYYY-MM}-{PILastName}-{GUP#}`` (e.g. ``2026-03-Li-1012039``).

For commissioning runs or staff experiments without a scheduling proposal, ``dmagic create-manual``
creates a DM experiment using badge numbers and metadata provided directly on the command line
(e.g. ``2026-03-Staff-0``).

Once an experiment is created, ``dmagic daq-start`` starts automated real-time file transfer:
the DM system monitors the experiment directory on the analysis machine (e.g.
``tomodata3:/data3/2BM/2026-03-Li-1012039``) and continuously transfers new files to Sojourner
as data is collected. ``dmagic daq-stop`` stops the transfer at the end of the run.

``dmagic add-user`` adds one or more users to an existing experiment by badge number,
and ``dmagic remove-user`` removes them, both prompting interactively if no badges are
provided on the command line.

``dmagic email`` sends a data-access notification email to all users on the experiment,
including the Globus URL to their data directory. Both proposal-based and manually created
experiments can be listed and removed using ``dmagic delete``.

DMagic is primarily used at tomography beamlines (e.g. 2-BM, 7-BM, 32-ID) in conjunction
with `tomoScan <https://tomoscan.readthedocs.io/>`_ to populate user information PVs and
manage data access at the start of each user run.
