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
                         If no proposal is found in the scheduling system, logs a clear
                         message and suggests running 'dmagic create-manual' followed by
                         'dmagic tag-manual'.

- dmagic tag-manual    : Interactively lists all DM experiments for the station (both
                         scheduling-based and manually created, sorted newest first) and
                         lets the operator choose which one to write to the EPICS PVs.
                         Useful for commissioning runs with no scheduling proposal, or
                         when sneaking in a sample from a different user group. For
                         non-zero GUP experiments it fetches full PI info from the
                         scheduling system; for manually created ones (GUP=0) it derives
                         the PI last name from the experiment name.

- dmagic create        : Creates a DM experiment on Sojourner for a proposal-based
                         beamtime. Lists all beamtimes in the current run, prompts for
                         selection, then creates the experiment and adds all proposal users.

- dmagic create-manual : Creates a DM experiment manually for commissioning runs or
                         staff experiments that have no scheduling proposal. PI name,
                         title, and optional badge numbers are provided on the command
                         line. Optional arguments:
                           --gup   GUP number (default: 0 = no proposal/commissioning)
                           --date  year-month in yyyy-mm format (default: current month)
                           --start experiment start date in yyyy-mm-dd format
                                   (default: first day of --date month)
                           --end   experiment end date in yyyy-mm-dd format
                                   (default: 14 days after --start)
                         Experiment name format: yyyy-mm-{LastName}-{gup}
                         Example: dmagic create-manual --name DeCarlo
                                    --first-name Francesco --gup 1
                                    --start 2026-05-01 --end 2026-05-07
                                    --title "2-BM commissioning"

- dmagic delete        : Deletes a DM experiment from Sojourner. Lists all experiments
                         for the station (last 2 years, including manually created ones)
                         and requires double confirmation before deleting.

- dmagic email         : Sends a data-access notification email with a Globus link to
                         all users on a DM experiment. Lists station experiments and
                         prompts for selection. The email includes a Google Slides
                         presentation URL, looked up in {tomolog-home}/.tomolog by
                         GUP number (most recent entry wins). Override with
                         --presentation-url URL when tomolog was not run yet or you
                         want to email a specific deck.

- dmagic daq-start     : Starts automated file transfer (DAQ) to Sojourner. On start,
                         the DM system uploads every file already present in the
                         experiment directory (raw and _rec), then continues to sync
                         new/changed files as they arrive. Runs until stopped with
                         'dmagic daq-stop'. Because it also handles pre-existing files,
                         it can be started at any time — before, during, or after the
                         acquisition — and will still catch every file.

- dmagic daq-stop      : Lists experiments that currently have running DAQs for the
                         station (skipping the full experiment list), and stops all
                         DAQs for the one you select. Exits cleanly if none are running.

- dmagic daq-status    : Lists all currently running DM DAQs for the station: experiment
                         name, source directory, files processed / total, percentage
                         complete, runtime, and DAQ id. Read-only.

- dmagic upload        : One-shot upload of all existing files in an experiment
                         directory to Sojourner. Now essentially redundant with
                         'dmagic daq-start' (which also uploads pre-existing files);
                         kept as a fallback for cases where daq-start was not running
                         during data collection.

- dmagic add-user      : Adds one or more users to an existing DM experiment by badge
                         number. Prompts interactively if no badges are provided on the
                         command line.

- dmagic remove-user   : Removes one or more users from an existing DM experiment by
                         badge number. Shows the current user list before prompting.

- dmagic list-users    : Lists all users currently granted access to a DM experiment,
                         including their DM username, full name, and email address.

- dmagic list-esafs    : Lists ESAFs for the beamline station in a date range using the
                         DM EsafApsDbApi. Options:
                           --start-date  range start in yyyy-mm-dd format
                                         (default: first day of current month)
                           --end-date    range end in yyyy-mm-dd format (default: today)
                         Output: one line per ESAF with id, status, start/end dates, title.

- dmagic list-beamtimes: Lists every beamtime scheduled on this beamline whose window
                         overlaps a date range, aggregated across all APS runs that
                         touch the range. Uses the APS scheduling REST API (not DM),
                         so a beamtime shows up whether or not a DM experiment was
                         ever created for it. Options:
                           --start-date  range start in yyyy-mm-dd format
                                         (default: January 1 of the current year)
                           --end-date    range end in yyyy-mm-dd format (default: today)
                         Output: one line per beamtime with start/end dates, run name,
                         GUP number, PI, and truncated proposal title.

- dmagic collected     : For each beamtime scheduled in [--start-date, --end-date],
                         reports whether a matching DM experiment on Sojourner exists
                         (and its name), or shows "(no DM experiment)" if nothing was
                         created. Joins scheduling beamtimes to DM experiments by GUP,
                         preferring same-month matches when a GUP has more than one
                         DM experiment. Reports only what DM can authoritatively
                         answer — it does not count files under /gdata. Options are
                         the same as list-beamtimes:
                           --start-date  (default: January 1 of the current year)
                           --end-date    (default: today)

Per-beamline configuration (2-BM, 7-BM, 32-ID, ...)
---------------------------------------------------

Defaults baked into config.py are 2-BM values. To install at another beamline,
run 'dmagic init' and then edit the [site] and [local] sections of
~/dmagic.conf with beamline-specific values (globus-server-uuid,
experiment-type, globus-message-file, primary/secondary contact badges and
emails, tomoscan-prefix, tomolog-home, plus [local] data-host and data-top-dir).

Full per-beamline lookup table (with Globus UUIDs and staff contacts for
2-BM, 7-BM, and 32-ID) and instructions for adding a new beamline are in
docs/source/usage.rst under 'Configuring for a different beamline'.

DM data-directory format
------------------------

The [local] config knob 'dm-direct-mount' controls how dmagic hands the
source path to the DM DAQ:

  - dm-direct-mount = True (default at 2-BM): dmagic passes the bare local
    path '{data-top-dir}/{exp-name}'. Correct when the DM VM already
    mounts the data filesystem directly (2-BM DM VM has both
    tomodata2:/data2 and tomodata3:/data3 mounted).

  - dm-direct-mount = False: dmagic passes
    '@{data-host}:{data-top-dir}/{exp-name}' — DM rsyncs from the
    data host over SSH. This form has a bug on the 2-BM DM installation
    where directory scans silently return countFiles=0 with
    "no new files for upload" even for directories with matching files,
    so leave the default (True) unless a future DM release fixes that.

Passwordless SSH prerequisite
-----------------------------

'dmagic upload' and 'dmagic daq-start' pre-check the source directory before
dispatching to DM. On beamline nodes that already mount the data top-dir
(tomo1, tomo3, tocai, ...) no setup is needed. On a control computer that does
NOT mount /data2 or /data3 (e.g. arcturus), dmagic falls back to an SSH probe
on the data host — set up passwordless SSH once:

    ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519    # only if no key yet
    ssh-copy-id tomodata2
    ssh-copy-id tomodata3

If SSH is not set up, dmagic prints a warning with the exact commands above
and dispatches to DM anyway (the pre-check is a safety net, not required).

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
