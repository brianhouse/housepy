import urllib.request
from . import log

def grab(source, destination, data=None, username=None, password=None, headers=None):
    read(source, data, username=username, password=password, headers=headers, filename=destination)

def read(source, data=None, timeout=30, username=None, password=None, headers=None, filename=None):
    """Filename is the name of the file to write"""
    request = urllib.request.Request(source)
    if data is not None:
        if type(data) == dict:
            data = urlencode(data).encode('utf-8')
        request.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
    if username and password:
        import base64
        auth = base64.b64encode('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % auth) 
    if headers:
        for header, value in headers.items():
            request.add_header(header, value)
    if filename is None:        
        f = urllib.request.urlopen(request, data, timeout=timeout) if data is not None else urllib.request.urlopen(request, timeout=timeout)
        response = f.read().decode('utf-8')
        return response
    else:
        result = urllib.request.urlretrieve(source, filename, None, data) if data is not None else urllib.request.urlretrieve(source, filename)

        
def urlencode(data):
    return urllib.parse.urlencode(data)

def urldecode(query_string):
    data = urllib.parse.parse_qs(query_string, keep_blank_values=True)
    for d in data:
        if len(data[d]) == 0:
            data[d] = ""
        elif len(data[d]) == 1:
            data[d] = data[d][0]
    return data
            
def validate_url(url):
    import re
    pattern = '^(http://|(www)\\.)[a-z0-9-]+(\\.[a-z0-9-]+)+([/?].*)?$'     ## does not support unicode
    return re.match(pattern, url) != None
