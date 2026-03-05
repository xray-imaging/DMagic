import os
import pathlib
import smtplib

from email.message import EmailMessage

from dmagic import log
from dmagic import dm


def yes_or_no(question):
    """Prompt the user for a Y/N answer. Returns True for yes, False for no."""
    answer = str(input(question + " (Y/N): ")).lower().strip()
    while answer not in ("y", "yes", "n", "no"):
        log.warning("Input yes or no")
        answer = str(input(question + " (Y/N): ")).lower().strip()
    return answer[0] == "y"


def _message_file_path(args):
    """Resolve the email template file path relative to this module's directory."""
    return os.path.join(pathlib.Path(__file__).parent, args.globus_message_file)


def message(args):
    """Read the email template, inject the current Globus data link, and return
    an EmailMessage object ready to send.

    The template file must contain a line starting with 'Data link:' which will
    be replaced with the actual Globus URL for the experiment.
    """
    msg_file = _message_file_path(args)
    with open(msg_file, 'r') as f:
        lines = f.readlines()

    data_link = dm.make_data_link(args)
    with open(msg_file, 'w') as f:
        for line in lines:
            if line.startswith('Data link:'):
                line = 'Data link: {:s}\n'.format(data_link)
            f.write(line)

    with open(msg_file, 'r') as f:
        msg = EmailMessage()
        msg.set_content(f.read())

    msg['From']    = args.primary_beamline_contact_email
    msg['Subject'] = 'Important information on APS experiment'
    return msg


def send_email(args):
    """Send the experiment data-access email to all users on the DM experiment.

    Prompts for confirmation before sending. SMTP sending is currently stubbed
    out — uncomment the smtplib block below when ready to enable.
    """
    log.info("Send email to users?")
    if not yes_or_no('   *** Yes or No'):
        log.warning('   *** Message not sent')
        return False

    users = dm.list_users_this_dm_exp(args)
    if users is None:
        log.error('   Cannot send email: no DM experiment found. Have you run "dmagic create" yet?')
        return False

    emails = dm.make_user_email_list(users)
    if not emails:
        log.warning('   No user emails found on the DM experiment')

    emails.append(args.primary_beamline_contact_email)
    emails.append(args.secondary_beamline_contact_email)

    log.info('   Would send email to: %s' % ', '.join(emails))

    # Uncomment the block below to enable actual email sending:
    s = smtplib.SMTP('mailhost.anl.gov')
    for em in emails:
        if args.msg['To'] is None:
            args.msg['To'] = em
        else:
            args.msg.replace_header('To', em)
        log.info('   Sending informational message to {:s}'.format(em))
        s.send_message(args.msg)
    s.quit()

    return True
