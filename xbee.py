#!/usr/bin/env python3

import serial, threading, time, os
from .lib.xbee import XBee as XB
from housepy import config, log

class XBee(threading.Thread):

    def __init__(self, device_name=None, baud=9600, message_handler=None, blocking=False, verbose=False):
        threading.Thread.__init__(self)
        self.daemon = True
        self.verbose = verbose
        self.message_handler = message_handler
        if device_name is None:
            for dn in os.listdir("/dev"):
                if "tty.usbserial-" in dn:
                    device_name = os.path.join("/dev", dn)
                    break
            if device_name is None:
                log.info("No devices available")
                exit()
        log.info("Receiving xbee messages on %s" % device_name)
        try:
            self.connection = serial.Serial(device_name, baud)
            self.xbee = XB(self.connection)
        except Exception as e:
            if e.message != "Port is already open.":
                log.error(log.exc(e))
                return
        self.start()
        if blocking:
            try:
                while True:
                    time.sleep(5)
            except (KeyboardInterrupt, SystemExit):
                self.connection.close()
                pass      

    def run(self):
        while True:
            try:
                data = self.xbee.wait_read_frame()
                if self.verbose:
                    log.debug(data)
                response = {}
                if 'source_addr' in data:
                    response['sensor'] = int(data['source_addr'][1])
                if 'frame_id' in data:
                    response['frame'] = str(data['frame_id'], 'ascii')
                if 'parameter' in data:
                    response['parameter'] = int.from_bytes(data['parameter'], 'little')
                if 'rssi' in data:
                    response['rssi'] = int.from_bytes(data['rssi'], 'little')
                if 'samples' in data:              
                    response['samples'] = []
                    for each in data['samples']:
                        samples = list(each.items())
                        samples.sort(key=lambda item: item[0])
                        response['samples'].append([s[1] for s in samples])
                    if len(response['samples']) == 1:
                        response['samples'] = response['samples'][0]
                if self.message_handler is not None:
                    self.message_handler(response)
            except Exception as e:
                log.error(log.exc(e))


if __name__ == "__main__":
    def message_handler(response):
        log.info(response)
    xbee = XBee(config['device_name'], message_handler=message_handler, blocking=True)



"""

XBee Setup
----------

#### NOTE: THIS IS SERIES 1
- install drivers (Mac OS X x64 2.2.18, for OS X 10.10.2): http://www.ftdichip.com/Drivers/VCP.htm  
- use X-CTU (http://www.digi.com/support/productdetail?pid=3352&type=utilities + http://support.apple.com/kb/DL1572?viewlocale=en_US&locale=en_US) to update firmware  

9600 baud, 8 bit, no parity, 1 stop bit, no flow control
(press the button when it asks!)

#### for coordinator
MY: 1  
CE: 1  
AP: 2  

#### for remote
DL: FFFF    (broadcast)  
MY: 2  -- or whatever number
AP: 2  
D2: 2       (analog)  
D1: 2  
D0: 2  
IT: 1       (samples before transmission)  
IR: 24       (sample rate, 36ms)

I like to get gestures at 60hz, which is 16.67ms
to signal process that, we'd need half the sample rate, 8ms.
but transmissions need to be staggered with multiple xbees. otherwise it floods.
for 30fs, 36ms sampling is definitely enough.
two sensors at 36ms is fine. but three at 36 overloads. xbee not so good for gestures :/

###### sleeping
SM: 5
ST: 1388 (5 seconds)    -- stay awake this long for communication
SP: 157C (55 seconds)   -- sleep for this long




use `ls /dev/tty.*` to find devices


#### addresses
- long address is the full 64-bit mac address printed on the back of the xbee, always starts with 0013A200 (for XBee brand)
- short address is 16-bit and is set with ATMY (series 2 assigns it automatically)


"""