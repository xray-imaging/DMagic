Project Home Page: http://dmagic.readthedocs.org/

dmagic (Data Magic) is a tool developed at Argonne National Laboratory for managing
experiment metadata at APS (Advanced Photon Source) beamlines. It bridges the APS
scheduling system (which tracks who is running experiments and when) with the EPICS
control system used to operate beamline equipment, and the APS Data Management (DM)
system (Sojourner) for experiment and user access management.

Key Commands
------------

- dmagic init          : Creates ~/dmagic.conf with default values for the beamline.

- dmagic show          : Queries the APS scheduling REST API to display the currently
                         active experiment's information: PI name, affiliation, email,
                         badge number, proposal ID/title, and start/end times.

- dmagic tag           : Fetches the same scheduling data and writes it into EPICS
                         Process Variables (PVs) on the beamline's TomoScan IOC.
                         Populates UserName, UserEmail, ProposalNumber, ProposalTitle, etc.

- dmagic create        : Creates a DM experiment on Sojourner for a proposal-based
                         beamtime. Lists all beamtimes in the current run, prompts for
                         selection, then creates the experiment and adds all proposal users.

- dmagic create-manual : Creates a DM experiment manually for commissioning runs or
                         staff experiments that have no scheduling proposal. Badge numbers,
                         PI name, and title are provided on the command line.

- dmagic delete        : Deletes a DM experiment from Sojourner. Lists all experiments
                         for the station (last 2 years, including manually created ones)
                         and requires double confirmation before deleting.

- dmagic email         : Sends a data-access notification email with a Globus link to
                         all users on a DM experiment. Lists station experiments and
                         prompts for selection.

- dmagic daq-start     : Starts automated real-time file transfer (DAQ) to Sojourner.
                         The DM system monitors the configured directory on the analysis
                         machine for new files and transfers them continuously.

- dmagic daq-stop      : Stops all running DAQs for a selected experiment.

- dmagic add-user      : Adds one or more users to an existing DM experiment by badge
                         number. Prompts interactively if no badges are provided on the
                         command line.

How It Works
------------

1. Authenticates against the APS scheduling REST API using stored credentials.
2. Determines the current APS run (e.g., "2026-1") based on the current date.
3. Finds the proposal(s) scheduled for the current beamline in that run.
4. Extracts PI and experiment metadata from the proposal.
5. Optionally writes that metadata to EPICS PVs so downstream data acquisition software
   (like TomoScan) can tag collected data with the correct experiment/user info.
6. Optionally creates a DM experiment on Sojourner, populates it with users from the
   scheduling proposal, starts automated file transfer (DAQ), and notifies users of
   their Globus data access link.

Use Case
--------

Primarily used at tomography beamlines (e.g., 2-BM, 7-BM, 32-ID) so that when a new
user group arrives to run their approved experiment, the beamline control system is
automatically updated with their identity and proposal information, ensuring data files
are properly attributed without manual entry. The DM integration automates creation of
data management experiments and notifies users of how to access their data via Globus.
