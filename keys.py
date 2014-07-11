#!/usr/bin/env python3

import sys, select, threading, time, tty, termios, atexit
from . import log, dispatcher

class Keys(threading.Thread, dispatcher.Dispatcher):
    
    def __init__(self):
        threading.Thread.__init__(self)
        dispatcher.Dispatcher.__init__(self)
        self.daemon = True
        self.old_settings = termios.tcgetattr(sys.stdin)        
        tty.setcbreak(sys.stdin.fileno())     
        atexit.register(self.restore)  
        self.start()
        
    def run(self):        
        while True:    
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                c = sys.stdin.read(1)
                if len(c.strip()):
                    # log.debug("got %s %s" % (c, ord(c)))
                    self.fire(ord(c))              
                    self.fire('key', c)
            time.sleep(0.01)

    def restore(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)                    
    

if __name__ == "__main__":        

    keys = Keys()

    def on_k():
        log.info("woo!")

    keys.add_callback(ord('k'), on_k)

    print("Press k")

    while True:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            keys.restore()
            break
            

    