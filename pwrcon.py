import asyncio
from kasa import Discover
import json
import psutil
import time
import win32evtlogutil
import win32evtlog
import psutil
import socket
import sys
import os
import atexit
import signal
import datetime

CONFIG_FILE = 'c:\pwrcon\config.json'

class PowerController:
    def __init__(self):
        self.load_config()
        self.running = True
        signal.signal(signal.SIGINT, self.kill_handler)
        signal.signal(signal.SIGTERM, self.kill_handler)

    def load_config(self):
        global CONFIG_FILE
        self.config = json.load(open(CONFIG_FILE))

    def log(self, message, event_type=win32evtlog.EVENTLOG_INFORMATION_TYPE):
        App_Name = "pwrcon"; App_Event_ID = 1034; App_Event_Category = 90
        if self.config['log_to_file']:
            file = open(self.conf['log_file'], 'a')
            file.write(f'\n {datetime.datetime.now()}: {message}')
            file.close()
        if event_type == win32evtlog.EVENTLOG_ERROR_TYPE:
            win32evtlogutil.ReportEvent(App_Name,App_Event_ID, eventCategory=App_Event_Category,eventType=event_type,strings=[f'{message}'],data=b"")
        print(f'{datetime.datetime.now()}: {message}')

    async def get_device(self):
        if os.path.isfile(self.config['device_config_file']):
            device_ip = open(self.config['device_config_file'],"r").read()
        else:
            device_ip = '255.255.255.255'
    
        self.log(f'Connecting to smart plug on {device_ip}')
    
        try:
            current_dev = await Discover.discover_single(device_ip,username=self.config['username'],password=self.config['password'])
            await current_dev.update()
            dev = current_dev
            self.log(f'Device connected on {device_ip}')
        except:
            self.log('Device not found. Re-scanning...')
            dev = await self.rescan()
        return dev

    async def rescan(self):
        bcast_addr = self.get_bcast_addr()
        found_devices = await Discover.discover(target=bcast_addr,username=self.config['username'],password=self.config['password'], discovery_timeout=5)
        for device in found_devices.values():
            if device.mac == self.config['mac']:
                dev_ip = device.host
                self.log(f'Device found on {dev_ip}')
                dev = await Discover.discover_single(dev_ip,username=self.config['username'],password=self.config['password'])
                await dev.update()
                f = open(self.config['device_config_file'], "w")
                f.write(dev_ip)
                f.close()
                self.log(f'Device IP saved to {self.config["device_config_file"]}')
                return dev

    def get_bcast_addr(self):
        self.log('Getting broadcast address')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
            s.close()
        except Exception:
            IP = '127.0.0.1'
            s.close()
        finally:
            s.close()
        bcast_addr = '.'.join(IP.split('.')[:-1]+["255"])
        return bcast_addr

    async def main(self):
        try:
            first_run = True
            while self.running:
                self.log(f'Loading config {CONFIG_FILE}')
                self.load_config()
                try_save_battery = not first_run
                dev = await self.get_device()
                battery = psutil.sensors_battery()
                for process in psutil.process_iter():
                    if process.name() in self.config['always_on_processes']:
                        self.log(f'Process {process.name()} found, keeping power on')
                        try_save_battery = False
                if try_save_battery:
                    if battery.percent < self.config['th_low']:
                        self.log(f'Host battery below {self.config["th_low"]}% - Powering on')
                        await dev.turn_on()
                        await dev.update()
                    if battery.percent > self.config['th_high']:
                        self.log(f'Host battery above {self.config["th_high"]}% - Powering off')
                        await dev.turn_off()
                        await dev.update()
                else:
                    await dev.turn_on()
                    await dev.update()
                self.log(f'Host battery {battery.percent}%. Smart plug {"on" if dev.is_on else "off"}. Finished, disconnecting, next check in {self.config["interval"]} seconds')
                await dev.disconnect()
                first_run = False
                await asyncio.sleep(self.config['interval'])
        except Exception as e:
            self.log(e, win32evtlog.EVENTLOG_ERROR_TYPE)
            self.log('Unhandled error. Retrying in 60 seconds...')
            time.sleep(60)
        return dev

    async def power_off_device(self):
        try:
            dev = await self.get_device()
            self.log('Powering off...')
            await dev.turn_off()
            await dev.update()
            await dev.disconnect()
        except Exception as e:
            self.log(f'Error while powering off the device: {e}', win32evtlog.EVENTLOG_ERROR_TYPE)

    def exit_handler(self):
        self.running = False
        asyncio.run(self.power_off_device())

    def kill_handler(self, *args):
        self.log('Killed by user')
        sys.exit(0)

    def start(self):
        self.log('Starting service...')
        atexit.register(self.exit_handler)
        asyncio.run(self.main())

controller = PowerController()
controller.start()