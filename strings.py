import re
from .timeutil import seconds_to_string as format_time

def format_size(bytes):
    try:
        bytes = float(bytes)
    except TypeError:
        return "0 bytes"
    if bytes < 1024:
        return "%d byte%s" % (bytes, bytes != 1 and 's' or '')
    if bytes < 1024 * 1024:
        return "%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return "%.1f MB" % (bytes / (1024 * 1024))
    return "%.1f GB" % (bytes / (1024 * 1024 * 1024))
            
def strip_html(s, keep_links=False):
    if keep_links:
        s = re.sub(r'</[^aA].*?>', '', s) 
        s = re.sub(r'<[^/aA].*?>', '', s)        
        return s
    else:    
        return re.sub(r'<.*?>', '', s)        
    
def singlespace(s): 
    p = re.compile(r'\s+')
    return p.sub(' ', s)    
    
def remove_linebreaks(s):
    s = s.splitlines()
    s = ' '.join(s)
    return singlespace(s).strip()
    
def depunctuate(s, exclude=None, replacement=''):
    import string
    p = string.punctuation
    if exclude:
        for c in exclude:
            p = p.replace(c, '')    
    regex = re.compile('[%s]' % re.escape(p))
    return regex.sub(replacement, s) 

def nl2br(s):
    return '<br />'.join(s.splitlines())       

def br2nl(s):
    return '\n'.join(s.split('<br />'))     
    
def slugify(value):
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[\s]+', '_', value)

def unslugify(value):
    value = value.replace('_', ' ')
    return titlecase(value)

def random_string(length=64):
    import random
    rs = []
    for i in range(length):
        rs.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))
    return ''.join(rs)        
    
def titlecase(value):
    return re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), value.title())

def camelcase(value):
    value = value.replace('_', ' ')
    tokens = value.split()
    return ''.join([token[0].upper() + token[1:] for token in tokens])
    
def linkify(text, extra_params=""):
    from tornado.escape import linkify
    return linkify(text, extra_params=extra_params)
    
def remove_non_ascii(s):        
    return "".join(i for i in s if ord(i) < 128)    
    
def as_numeric(s):
    if type(s) == int or type(s) == float or type(s) == bool:
        return s
    try:
        s = int(s)
    except (ValueError, TypeError):
        try:
            s = float(s)
        except (ValueError, TypeError):
            pass
    return s

    