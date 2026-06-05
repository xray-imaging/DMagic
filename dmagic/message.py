import os
import re
import pathlib
import smtplib

from email.message import EmailMessage
from html.parser import HTMLParser

from dmagic import log
from dmagic import dm


def yes_or_no(question):
    """Prompt the user for a Y/N answer. Returns True for yes, False for no."""
    answer = str(input(question + " (Y/N): ")).lower().strip()
    while answer not in ("y", "yes", "n", "no"):
        log.warning("Input yes or no")
        answer = str(input(question + " (Y/N): ")).lower().strip()
    return answer[0] == "y"


class _HtmlToTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts   = []
        self._skip    = 0
        self._in_ol   = False
        self._ol_idx  = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self._skip += 1
        elif tag in ('p', 'div', 'h1', 'h2', 'h3'):
            self._parts.append('\n')
        elif tag == 'br':
            self._parts.append('\n')
        elif tag == 'ol':
            self._in_ol = True
            self._ol_idx = 0
            self._parts.append('\n')
        elif tag == 'ul':
            self._in_ol = False
            self._parts.append('\n')
        elif tag == 'li':
            if self._in_ol:
                self._ol_idx += 1
                self._parts.append('\n%d. ' % self._ol_idx)
            else:
                self._parts.append('\n- ')

    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self._skip -= 1
        elif tag in ('p', 'div', 'ol', 'ul'):
            self._parts.append('\n')

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self):
        text = ''.join(self._parts)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


def html_to_text(html_content):
    """Strip HTML tags and return a readable plain-text version."""
    parser = _HtmlToTextParser()
    parser.feed(html_content)
    return parser.get_text()


def _message_file_path(args):
    """Resolve the email template file path relative to this module's directory."""
    return os.path.join(pathlib.Path(__file__).parent, args.globus_message_file)


def message(args):
    """Read the email template, inject the current Globus data link, and return
    an EmailMessage object ready to send.

    Supports two template formats:
    - HTML templates (file starts with '<html'): use %%DATA_LINK%% as placeholder;
      sent as a multipart/alternative HTML email.
    - Plain-text templates: must contain a line starting with 'Data link:';
      sent as plain text.
    """
    msg_file = _message_file_path(args)
    with open(msg_file, 'r') as f:
        content = f.read()

    data_link = dm.make_data_link(args)
    is_html = content.lstrip().startswith('<')

    if is_html:
        content = content.replace(
            '%%DATA_LINK%%',
            '<a href="{0}">{0}</a>'.format(data_link))
        slides_url = getattr(args, 'presentation_url', None)
        if slides_url:
            slides_html = '<a href="{0}">{0}</a>'.format(slides_url)
        else:
            slides_html = '(no beamtime log slides found for this proposal)'
        content = content.replace('%%SLIDES_LINK%%', slides_html)
    else:
        lines = content.splitlines(keepends=True)
        content = ''.join(
            'Data link: {:s}\n'.format(data_link) if line.startswith('Data link:') else line
            for line in lines)

    msg = EmailMessage()
    if is_html:
        msg.set_content('Please enable HTML to view this email.')
        msg.add_alternative(content, subtype='html')
    else:
        msg.set_content(content)

    exp_name = getattr(args, '_exp_name', '')
    if exp_name:
        subject = 'Important information for APS experiment {}'.format(exp_name)
    else:
        subject = 'Important information for APS experiment'

    msg['From']    = args.primary_beamline_contact_email
    msg['Subject'] = subject
    return msg


def _send_prompt():
    """Prompt Y / N / T (test).  Returns 'y', 'n', or 't'."""
    log.info("Send email to users?")
    answer = str(input('   *** Yes / No / Test (Y/N/T): ')).lower().strip()
    while answer not in ('y', 'yes', 'n', 'no', 't', 'test'):
        log.warning("Input Y (send to all), N (cancel), or T (test: send only to secondary beamline contact)")
        answer = str(input('   *** Yes / No / Test (Y/N/T): ')).lower().strip()
    return answer[0]


def send_email(args):
    """Send the experiment data-access email to all users on the DM experiment.

    Prompts for Y (send to all), N (cancel), or T (test: secondary beamline contact only).
    """
    choice = _send_prompt()

    if choice == 'n':
        log.warning('   *** Message not sent')
        return False

    if choice == 't':
        emails = [args.secondary_beamline_contact_email]
        log.info('   *** TEST mode: sending only to secondary beamline contact')
        s = smtplib.SMTP('mailhost.anl.gov')
        for em in emails:
            if args.msg['To'] is None:
                args.msg['To'] = em
            else:
                args.msg.replace_header('To', em)
            log.info('   Sending informational message to {:s}'.format(em))
            try:
                s.send_message(args.msg)
            except smtplib.SMTPRecipientsRefused as e:
                for addr, (code, msg) in e.recipients.items():
                    log.warning('   Skipping {:s}: {:d} {:s}'.format(addr, code, msg.decode()))
        s.quit()
        return False  # test send does not update emailed-users record
    else:
        # Use pre-filtered user list if set by the caller (e.g. new-users-only mode)
        user_filter = getattr(args, '_user_filter', None)
        if user_filter is not None:
            users = user_filter
        else:
            users = dm.list_users_this_dm_exp(args)
            if users is None:
                log.error('   Cannot send email: no DM experiment found. Have you run "dmagic create" yet?')
                return False

        emails = dm.make_user_email_list(users)
        if not emails:
            log.warning('   No user emails found on the DM experiment')

        for contact in (args.primary_beamline_contact_email,
                        args.secondary_beamline_contact_email):
            if contact not in emails:
                emails.append(contact)

    s = smtplib.SMTP('mailhost.anl.gov')
    any_sent = False
    for em in emails:
        if args.msg['To'] is None:
            args.msg['To'] = em
        else:
            args.msg.replace_header('To', em)
        log.info('   Sending informational message to {:s}'.format(em))
        try:
            s.send_message(args.msg)
            any_sent = True
        except smtplib.SMTPRecipientsRefused as e:
            for addr, (code, msg) in e.recipients.items():
                log.warning('   Skipping {:s}: {:d} {:s}'.format(addr, code, msg.decode()))
    s.quit()

    return any_sent
