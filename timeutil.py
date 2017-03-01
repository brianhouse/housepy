""" The following functions work together to provide a means of converting from arbitrary date strings 
    to UTC timestamps and back to uniformly formatted strings while handling time zones -- no naivete.
    """

import math, pickle, time, datetime, pytz, calendar
from dateutil import parser

def t_utc(dt=None, ms=False):
    """Return a UTC timestamp indicating the current time, or convert from a datetime. If datetime is naive, it's assumed to be UTC"""
    tz = pytz.timezone('UTC')
    if dt is None:
        dt = datetime.datetime.now(tz)
    elif dt.tzinfo is not None:
        dt = dt.astimezone(tz)
    t = calendar.timegm(dt.timetuple()) # assumes UTC
    return int(t) if not ms else t + (dt.microsecond / 1000000.0)

def get_string(t=None, tz='America/New_York', ms=False):
    """Return a string with the formatted date from a UTC timestamp, convert to given tz"""
    if t is None:
        t = t_utc()
    utc_z = pytz.timezone('UTC')
    dt = utc_z.localize(datetime.datetime.utcfromtimestamp(t))
    format = "%Y-%m-%dT%H:%M:%S%z" if not ms else "%Y-%m-%dT%H:%M:%S.%f%z"
    datestring = dt.astimezone(pytz.timezone(tz)).strftime(format)
    return datestring

def get_dt(t=None, tz='UTC'):
    """Get a datetime with the given tz from a UTC timestamp"""
    if t is None:
        t = t_utc()
    utc_z = pytz.timezone('UTC')
    dt = utc_z.localize(datetime.datetime.utcfromtimestamp(t))
    dt = dt.astimezone(pytz.timezone(tz))
    return dt

def t_to_utc(lt, tz='America/New_York'):
    """Convert a local timestamp to UTC"""
    tz = pytz.timezone(tz)
    dt = tz.localize(datetime.datetime.utcfromtimestamp(lt))
    return t_utc(dt)

def string_to_dt(string, tz='UTC', dayfirst=False):
    """Return a datetime with a best guess of the supplied string, using dateutil, and add tzinfo"""
    date = None
    try:
        date = parser.parse(string, dayfirst=dayfirst)
    except (ValueError, AttributeError) as e:
        try:
            date = get_dt(int(string), tz=tz) # is it a timestamp? If not, raise original error.
        except ValueError:
            pass
        if date is None:
            raise e            
    tz = pytz.timezone(tz)
    if date.tzinfo is None:
        date = tz.localize(date)
    else:
        date = date.astimezone(tz)
    return date

def format_seconds(seconds):
    if type(seconds) != int:
        seconds = float(seconds)
    minutes = int(seconds // 60)
    seconds = seconds - (minutes * 60)        
    hours = minutes // 60
    minutes = minutes - (hours * 60)        
    days = int(hours // 24)
    hours = int(hours - (days * 24))
    time = []
    if days:
        time.append("%s:" % days)
    if hours or days:
        time.append("%s:" % str(hours).zfill(2))
    if minutes or hours or days:
        time.append("%s:" % str(minutes).zfill(2))
    if type(seconds) == int:    
        if not minutes and not hours and not days:
            time.append(":%s" % str(seconds).zfill(2))        
        elif seconds or minutes or hours or days:
            time.append("%s" % str(seconds).zfill(2))
    else:
        if not minutes and not hours and not days:
            time.append(":%s" % str("%f" % seconds).zfill(2))        
        elif seconds or minutes or hours or days:
            time.append("%s" % str("%f" % seconds).zfill(2))
    time = "".join(time)               
    return time