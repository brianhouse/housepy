import tinys3, os, urllib
from . import config, log

""" Boto doesn't work with Python 3, so until it does, here are some stopgaps, thx tinys3.

"""

connection = tinys3.Connection(config['s3']['access_key_id'], config['s3']['secret_access_key'])

def download(source, destination=None):
    """Download from s3. This is pretty naive and doesn't use authentication, so has to be public."""
    if destination is None:
        destination = source
    if os.path.isdir(destination):
        destination = os.path.join(destination, source)
    log.info("s3 download: %s:%s -> %s" % (config['s3']['bucket'], source, destination))
    url = "http://%s.s3.amazonaws.com/%s" % (config['s3']['bucket'], source)
    result = urllib.request.urlretrieve(url, destination)

def upload(source, destination=None):
    if destination is None:
        destination = source.split('/')[-1]
    log.info("s3 upload: %s -> %s:%s" % (source, config['s3']['bucket'], destination))        
    with open(source, 'rb') as f:
        connection.upload(destination, f, config['s3']['bucket'])

def delete(filename):
    log.info("s3 delete: %s:%s" % (config['s3']['bucket'], filename))
    connection.delete(filename, config['s3']['bucket'])
