#!/usr/bin/env python

import pickle, inspect, sys, os, subprocess, time, platform, traceback
from . import config, log, process
from .lib import beanstalkc

"""
beanstalk:
    address: 0.0.0.0
    port: 11238
    bin: /opt/local/bin/beanstalkd
    pid: /Users/house/Projects/openpaths/run/beanstalkd.pid

"""

class Jobs(object): # having this in a class allows control over connection time
        
    def __init__(self):
        address = config['beanstalk']['address']
        port = config['beanstalk']['port']
        try:
            log.info("Jobs instance connecting to beanstalk (%s:%s)..." % (address, port))
            self.queue = beanstalkc.Connection(host=address, port=port)
            log.info("--> connected")
        except Exception as e:
            log.error("--> could not connect: %s" % log.exc(e))
            self.queue = None
            
    def close(self):
        self.queue.close()                    
        
    def add(self, tube=None, data=None, timeout=120, verbose=True):
        """Add a job to the specified tube."""        
        if self.queue is None:
            log.error("Attempted to add job, but job queue is not running")
            return
        if tube is not None:
            self.queue.use(tube)
        if verbose:
            log.info("Jobs.add tube[%s] data[%s]" % (self.queue.using(), data))
        self.queue.put(pickle.dumps(data), ttr=timeout)
                
    def process(self, handler=None, tube=None, num_jobs=0):  
        """Process all jobs in the specified tube. Blocking."""
        if self.queue is None:
            log.error("Attempted to process tube, but job queue is not running")
            return
        if tube is not None:
            self.queue.watch(tube)        
        log.info("Starting Jobs.process [%s] ..." % self.queue.watching())
        while True:            
            job = self.queue.reserve() # no timeout will block until a job is found. timeout=0 will fire it immediately and not block
            if job:
                # log.info("Jobs.process: got job")
                data = pickle.loads(job.body)
                try:
                    if handler(data) != False:   # use a handler to process the data
                        job.delete()
                        # log.info("--> complete")                            
                    else:
                        job.bury()
                        log.warning("Job buried")
                except Exception as e:
                    log.error("Job error: %s" % traceback.format_exc())
                    try:                            
                        job.bury()  # at this stage, beanstalk can fail, so it needs to be caught
                    except Exception as e:
                        pass
                    log.warning("Job buried")                                         
            else:
                log.warning("No jobs")
            if num_jobs:
                if num_jobs == 1:
                    log.info("Job cycle complete, exiting")                                        
                    return
                else:
                    num_jobs -= 1
                    log.info("Will process %s more jobs" % num_jobs)
                                        
    def stall(self, tube=None):
        """Bury all jobs in a tube."""
        if self.queue is None:
            log.error("Attempted to stall tube, but job queue is not running")
            return
        log.info("Jobs.stall [%s] ..." % tube)            
        if self.queue.peek_ready() is not None:                    
            self.queue.watch(tube)    
            d = 0
            while True:
                job = self.queue.reserve(timeout=0)
                if job is None:
                    break
                job.bury()
                d += 1
            log.info("--> buried %s jobs" % d)
        else:
            log.info("--> nothing queued")       

    def skip(self, tube=None):
        """Skip all jobs in a tube."""
        if self.queue is None:
            log.error("Attempted to skip tube, but job queue is not running")
            return
        log.info("Jobs.skip [%s] ..." % tube)            
        if self.queue.peek_ready() is not None:                    
            self.queue.watch(tube)    
            d = 0
            while True:
                job = self.queue.reserve(timeout=0)
                if job is None:
                    break
                job.delete()
                d += 1
            log.info("--> skipped %s jobs" % d)
        else:
            log.info("--> nothing queued")

    def kick(self, tube=None):
        """Restart all buried jobs in a tube."""        
        if self.queue is None:
            log.error("Attempted to kick tube, but job queue is not running")
            return
        if tube is not None:
            self.queue.use(tube)
        log.info("Jobs.kick [%s] ..." % tube)
        if self.queue.peek_buried() is not None:
            self.queue.kick() 
            log.info("--> kicked")
        else:
            log.info("--> nothing buried")       
                    
    def dump(self, tube=None):
        """Delete all buried jobs in a tube."""                
        if self.queue is None:
            log.error("Attempted to dump tube, but job queue is not running")
            return
        if tube is not None:
            self.queue.use(tube)
        log.info("Jobs.dump [%s] ..." % tube)
        d = 0
        while True:
            job = self.queue.peek_buried()
            if job is None:
                break
            job.delete()
            d += 1
        log.info("--> dumped %s jobs" % d)            
                           
    def clear(self, tube=None):
        """Clear all jobs, ready or buried, in the tube"""
        self.stats(tube)
        self.kick(tube)
        self.stall(tube)
        self.dump(tube)      

    def stats(self, tube=None):
        """Display stats"""
        if self.queue is None:
            log.error("Attempted to show stats, but job queue is not running") 
            return
        if tube is not None:
            self.queue.use(tube)            
        log.info("Jobs.stats [%s] ..." % tube)            
        if tube is None:
            stats = self.queue.stats()
        else:
            stats = self.queue.stats_tube(tube)
            connection_stats = {}
            for stat in stats:
                if stat[:13] == 'current-jobs-':
                    connection_stats[stat[13:]] = stats[stat]
            stats = connection_stats        
        log.info("--> %s" % stats)
        return stats

        
def launch_beanstalkd():
    
    """Note that this keeps beanstalkd within this python process, so be careful if you have multiple daemons."""
    
    def write_pidfile(pid, pidfile):    
        f = open(pidfile, 'w')
        f.write(str(pid))
        f.close()
    
    pidfile = config['beanstalk']['pid']
    bin = config['beanstalk']['bin']
    log.info("Launching beanstalkd...")

    pid = process.get_pid(bin)
    if pid:
        log.info("--> %s already running with pid %s" % (bin, pid))
        write_pidfile(pid, pidfile)
        return True

    subprocess.check_call("exec %s -l %s -p %s &" % (config['beanstalk']['bin'], config['beanstalk']['address'], config['beanstalk']['port']), shell=True)        
    time.sleep(0.25)
    pid = process.get_pid(bin)
    if not pid:
        log.error("--> could not launch beanstalkd")
        return False        
    log.info("--> %s now running with pid %s" % (bin, pid))
    write_pidfile(pid, pidfile)
        
    return True
