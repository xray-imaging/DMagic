Project Home Page: http://dmagic.readthedocs.org/

dmagic (Data Magic) is a tool developed at Argonne National Laboratory for managing
experiment metadata at APS (Advanced Photon Source) beamlines. It bridges the APS
scheduling system (which tracks who is running experiments and when) with the EPICS
control system used to operate beamline equipment.

Key Commands
------------

- dmagic show  : Queries the APS scheduling REST API to display the currently active
                 experiment's information: PI name, affiliation, email, badge number,
                 proposal ID/title, and start/end times.

- dmagic tag   : Fetches the same scheduling data and writes it into EPICS Process
                 Variables (PVs) on the beamline's TomoScan IOC. This populates fields
                 like UserName, UserEmail, ProposalNumber, ProposalTitle, etc. in real-time.

- dmagic init  : Creates a configuration file.

How It Works
------------

1. Authenticates against the APS scheduling REST API using stored credentials.
2. Determines the current APS run (e.g., "2024-1") based on the current date.
3. Finds the proposal scheduled for the current beamline at the current time.
4. Extracts PI and experiment metadata from the proposal.
5. Optionally writes that metadata to EPICS PVs so downstream data acquisition software
   (like TomoScan) can tag collected data with the correct experiment/user info.

Use Case
--------

Primarily used at tomography beamlines (e.g., 2-BM, 7-BM, 32-ID) so that when a new
user group arrives to run their approved experiment, the beamline control system is
automatically updated with their identity and proposal information, ensuring data files
are properly attributed without manual entry.
