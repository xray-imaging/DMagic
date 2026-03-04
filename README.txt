Project Home Page: http://dmagic.readthedocs.org/

dmagic (Data Magic) is a tool developed at Argonne National Laboratory for managing
experiment metadata at APS (Advanced Photon Source) beamlines. It bridges the APS
scheduling system (which tracks who is running experiments and when) with the EPICS
control system used to operate beamline equipment, and the APS Data Management (DM)
system (Sojourner) for experiment and user access management.

Key Commands
------------

- dmagic show   : Queries the APS scheduling REST API to display the currently active
                  experiment's information: PI name, affiliation, email, badge number,
                  proposal ID/title, and start/end times.

- dmagic tag    : Fetches the same scheduling data and writes it into EPICS Process
                  Variables (PVs) on the beamline's TomoScan IOC. This populates fields
                  like UserName, UserEmail, ProposalNumber, ProposalTitle, etc. in real-time.

- dmagic create : Creates a DM experiment on Sojourner and adds all users listed in the
                  APS scheduling proposal. Lists all beamtimes in the current run and
                  prompts for selection. Supports --manual mode for commissioning runs.

- dmagic email  : Sends a data-access notification email to all users on the DM experiment,
                  including a Globus link to the experiment data directory.

- dmagic init   : Creates a configuration file.

How It Works
------------

1. Authenticates against the APS scheduling REST API using stored credentials.
2. Determines the current APS run (e.g., "2024-1") based on the current date.
3. Finds the proposal(s) scheduled for the current beamline in that run.
4. Extracts PI and experiment metadata from the proposal.
5. Optionally writes that metadata to EPICS PVs so downstream data acquisition software
   (like TomoScan) can tag collected data with the correct experiment/user info.
6. Optionally creates a DM experiment on Sojourner and populates it with the users
   from the scheduling proposal, enabling Globus data access.

Use Case
--------

Primarily used at tomography beamlines (e.g., 2-BM, 7-BM, 32-ID) so that when a new
user group arrives to run their approved experiment, the beamline control system is
automatically updated with their identity and proposal information, ensuring data files
are properly attributed without manual entry. The DM integration further automates
creation of data management experiments and notifies users of how to access their data
via Globus.
