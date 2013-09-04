import smtplib, os, imaplib, email, mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders, utils
from . import config, log, strings, util

"""
email:
    imap:
        server: mail.messagingengine.com
        username: un
        password: pp
    smtp:
        name: Dr. H
        address: account@email.com
        server: smtp.gmail.com
        port: 587
        username: un
        password: pp

//

messages = emailer.fetch()
for message in messages:
    print(message['from'])
    print(message['to'])
    print(message['date'])
    print(message['subject'])
    if 'body' in message:
        print(message['body'])
    if 'html' in message:
        print(message['html'])
    for attachment in message['attachments']:
        with open(attachment['filename'], 'wb') as f:
            f.write(attachment['data'])
"""

"""Include all functions in string module as jinja2 filters"""
filters = {}
for function_name in dir(strings):
    if '__' in function_name:
        continue
    filters[function_name] = eval("strings." + function_name)
# note nice built-in filters: int, e (html_escape)

def send_from_template(addresses, subject, template_name, template_values=None, attachment=None):
    log.info("emailer.send_from_template (%s)" % template_name)
    from jinja2.exceptions import TemplateNotFound    
    try:
        html = render(template_name, template_values)
    except TemplateNotFound:
        log.error("HTML template not found (%s)" % template_name)
        html = None
    try:    
        text = render(template_name, template_values, suffix="txt")      
        text = strings.safestr(text)
    except TemplateNotFound:
        log.error("TXT template not found (%s)" % template_name)
        text = None
    return send(addresses, subject, text, html, attachment)

def send(addresses, subject, text, html=None, attachment=None):
    log.info("emailer.send [%s] [%s]" % (addresses, subject))   
    if isinstance(addresses, str):
        addresses = [r.strip() for r in addresses.split(',')]
    account = config['email']['smtp']
    if html:
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(text, 'plain'))  
        msg.attach(MIMEText(html, 'html'))
    else:
        msg = MIMEText(text, 'plain')
    if attachment:
        tmpmsg = msg
        msg = MIMEMultipart()
        msg.attach(tmpmsg)
        msg.attach(MIMEText("\n\n", 'plain')) # helps to space the attachment from the body of the message
        log.info("--> adding attachment")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment))
        msg.attach(part)                
    sender = account['name'] + " <" + account['address'] + ">"
    msg['From'] = sender
    msg['To'] = ','.join(addresses)
    msg['Subject'] = subject
    try:
        server = smtplib.SMTP(account['server'], account['port'])
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(account['username'], account['password'])
        server.sendmail(sender, addresses, msg.as_string())
        server.close()
    except Exception as e:
        log.error("Could not send email (%s)" % log.exc(e))
        return False
    return True    

def render(template_name, template_values=None, suffix="html"):
    if template_values is None: template_values = {}        
    template_values['template_name'] = template_name
    log.info("TEMPLATE %s.%s: %s" % (template_name, suffix, template_values))        
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates/"))    
    renderer = render_jinja(template_dir)      
    renderer._lookup.filters.update(filters.filters)
    return renderer[template_name + "." + suffix](template_values)       

class render_jinja:

    def __init__(self, *a, **kwargs):
        extensions = kwargs.pop('extensions', [])
        globals = kwargs.pop('globals', {})

        from jinja2 import Environment, FileSystemLoader
        self._lookup = Environment(loader=FileSystemLoader(*a, **kwargs), extensions=extensions)
        self._lookup.globals.update(globals)

    def __getitem__(self, name):
        t = self._lookup.get_template(name)
        return t.render
        
        
def validate_address(emailaddress):
    """Returns True if the supplied string is a valid email address"""
    domains = 'ac', 'ad', 'ae', 'aero', 'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'aq', 'ar', 'arpa', 'as', 'asia', 'at', 'au', 'au', 'aw', 'ax', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'biz', 'bj', 'bl', 'bm', 'bn', 'bo', 'bq', 'br', 'bs', 'bt', 'bv', 'bw', 'by', 'bz', 'ca', 'cat', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'co', 'com', 'coop', 'cr', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'edu', 'ee', 'eg', 'eh', 'er', 'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gov', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'info', 'int', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jobs', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 'mil', 'mk', 'ml', 'mm', 'mn', 'mo', 'mobi', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'museum', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'name', 'nc', 'ne', 'net', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'org', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'pro', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'ss', 'st', 'su', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tel', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'travel', 'tt', 'tv', 'tw', 'tz', 'ua', 'ug', 'uk', 'um', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu', 'wf', 'ws', 'xxx', 'ye', 'yt', 'za', 'zm', 'zw'
    if len(emailaddress) < 7:
        return False # Address too short.
    try:
        localpart, domainname = emailaddress.rsplit('@', 1)
        host, toplevel = domainname.rsplit('.', 1)
    except ValueError:
        return False # Address does not have enough parts.
    if len(toplevel) != 2 and toplevel not in domains:
        return False # Not a domain name.
    for i in '-_.%+.':
        localpart = localpart.replace(i, "")
    for i in '-_.':
        host = host.replace(i, "")
    if localpart.isalnum() and host.isalnum():
        return True # Email address is fine.
    else:
        return False # Email address has funny characters.        
        
def fetch(delete=False):
    server = imaplib.IMAP4_SSL(config['email']['imap']['server'])
    server.login(config['email']['imap']['username'], config['email']['imap']['password'])
    server.select('INBOX')
    response, items = server.search(None, "(UNSEEN)")
    messages = []
    for mail in items[0].split():
        try:
            response, data = server.fetch(mail, '(RFC822)')            
            data = email.message_from_bytes(data[0][1])
            message = { 'to': utils.parseaddr(data['to'])[-1],
                        'from': utils.parseaddr(data['from'])[-1],
                        'subject': data['subject'],
                        'date': util.parse_date(data['date']),
                        'attachments': []
                        }
            for part in data.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_content_type() == 'text/plain':
                    message['body'] = part.get_payload(decode=True).strip().decode(part.get_content_charset())
                if part.get_content_type() == 'text/html':
                    message['html'] = part.get_payload(decode=True).strip().decode(part.get_content_charset())
                filename = part.get_filename()
                if filename:
                    message['attachments'].append({'filename': filename, 'data': part.get_payload(decode=True)})
            messages.append(message)
            if delete:
                server.store(mail, '+FLAGS', '\\Deleted')
            else:
                server.store(mail, '+FLAGS', '\\Seen')
        except Exception as e:
            log.error(log.exc(e))
    if delete:
        server.expunge()
    return messages        

if __name__ == "__main__":
    print(fetch())
        
