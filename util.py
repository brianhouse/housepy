import math, pickle, time, datetime, pytz, calendar
from dateutil import parser
from .timeutil import string_to_dt as parse_date
from .timeutil import t_utc as timestamp
from .timeutil import get_string as datestring
from .timeutil import get_dt as dt
from .timeutil import t_to_utc as delocalize_timestamp

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

def save(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
        