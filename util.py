import math

def num_args(f):
    """Returns the number of arguments received by the given function"""
    import inspect
    return len(inspect.getargspec(f).args)  
        
def soup(string, **kwargs):
    """Create a BeautifulSoup parse object from a string"""
    from bs4 import BeautifulSoup
    return BeautifulSoup(string, **kwargs)
    
def chunk(l, size):    
    def ck(l, size):
        for i in range(0, len(l), size):
            yield l[i:i + size] 
    return list(ck(l, size))

def scale(value, in_min, in_max, out_min=0.0, out_max=1.0, limit=False):
    """Scales a value between the given min/max to a new min/max, default 0.0-1.0. If limit is True, limit the value to the min/max."""
    value = (value - in_min) / (in_max - in_min)
    if out_min != 0.0 or out_max != 1.0:
        value *= out_max - out_min
        value += out_min
    if limit:    
        if value > out_max:
            value = out_max
        elif value < out_min:
            value = out_min        
    return value

def distance(a, b):
    """Euclidean distance between two sequences"""
    assert len(a) == len(b)    
    t = sum((a[i] - b[i])**2 for i in range(len(a)))
    return math.sqrt(t)

def hamming_distance(a, b):
    """Hamming distance between two sequences (edit distance that only allows substitutions)"""
    assert len(a) == len(b)
    return sum(ch_a != ch_b for ch_a, ch_b in zip(a, b))

def weighted_hamming_distance(a, b):
    """Hamming distance between two sequences (edit distance that only allows substitutions) preserving the degree of substitution"""
    assert len(a) == len(b)
    return sum(abs(ch_a - ch_b) for ch_a, ch_b in zip(a, b))
    
def lev_distance(a, b):
    """Levenshtein distance between two sequences (edit distance that allows substitutions, adds, and deletions)"""    
    if len(a) < len(b):
        return lev_distance(b, a)
    previous_row = range(len(b) + 1)
    for i, ch_a in enumerate(a):
        current_row = [i + 1]
        for j, ch_b in enumerate(b):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer than b
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (ch_a != ch_b)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]    

def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:      
        a, b = b, a % b
    return a

def lcm(a, b):
    """Return lowest common multiple."""
    return a * b / gcd(a, b)


""" The following functions work together to provide a means of converting from arbitrary date strings 
    to UTC timestamps and back to uniformly formatted strings while handling time zones -- no naivete.
    """

def parse_date(string, tz='UTC', dayfirst=False):
    """Return a datetime with a best guess of the supplied string, using dateutil, and add tzinfo"""
    import pytz
    from dateutil import parser
    dt = parser.parse(string, dayfirst=dayfirst)
    tz = pytz.timezone(tz)
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)
    return dt

def timestamp(dt=None, ms=False):
    """Return a UTC timestamp indicating the current time, or convert from a datetime. If datetime is naive, it's assumed to be UTC"""
    import time, datetime, pytz, calendar
    tz = pytz.timezone('UTC')
    if dt is None:
        dt = datetime.datetime.now(tz)
    elif dt.tzinfo is not None:
        dt = dt.astimezone(tz)
    t = calendar.timegm(dt.timetuple()) # assumes UTC
    return int(t) if not ms else float("%s.%s" % (t, dt.microsecond))

def datestring(t=None, tz="America/New_York", ms=False):
    """Return a string with the formatted date from a UTC timestamp, convert to given tz"""
    import time, datetime, pytz
    if t is None:
        t = timestamp()
    utc_z = pytz.timezone('UTC')
    dt = utc_z.localize(datetime.datetime.utcfromtimestamp(t))
    format = "%Y-%m-%dT%H:%M:%S%z" if not ms else "%Y-%m-%dT%H:%M:%S.%f%z"
    datestring = dt.astimezone(pytz.timezone(tz)).strftime(format)
    return datestring


