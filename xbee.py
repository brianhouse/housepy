#!/usr/bin/env python3

import serial, threading, time, os
from .lib.xbee import XBee as XB
from housepy import config, log

class XBee(threading.Thread):

    def __init__(self, device_name=None, baud=9600, message_handler=None, blocking=False):
        threading.Thread.__init__(self)
        self.daemon = True
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
                # log.debug(data)
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
                    response['samples'] = [data['samples'][0][key] for key in data['samples'][0]]
                if self.message_handler is not None:
                    self.message_handler(response)
            except Exception as e:
                log.error(log.exc(e))


if __name__ == "__main__":
    def message_handler(response):
        log.info(response)
    xbee = XBee(config['device_name'], message_handler=message_handler, blocking=True)

