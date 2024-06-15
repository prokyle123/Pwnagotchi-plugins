import os
import time
import logging
import pigpio
from pwnagotchi.plugins import Plugin
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from threading import Thread

class FanControl(Plugin):
    __author__ = "Kyle Williams"
    __version__ = "1.0.3"
    __license__ = "GPL3"
    __description__ = "A plugin to control a PWM fan based on CPU temperature and display fan speed and RPM."

    def __init__(self):
        self.running = True
        self.pi = None
        self.FAN_GPIO = 18
        self.TACH_GPIO = 23
        self.fan_speed = 0
        self.last_tick = 0
        self.tick_count = 0
        self.rpm = 0
        logging.info("FanControl: Initialized")

    def on_loaded(self):
        logging.info("FanControl: Plugin loaded")
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                raise Exception("Failed to connect to pigpio daemon")
            self.pi.set_mode(self.TACH_GPIO, pigpio.INPUT)
            self.pi.set_pull_up_down(self.TACH_GPIO, pigpio.PUD_UP)
            self.pi.callback(self.TACH_GPIO, pigpio.FALLING_EDGE, self.tach_callback)
            self.running = True
            self._thread = Thread(target=self.run, daemon=True)
            self._thread.start()
            logging.info("FanControl: Background thread started")
        except Exception as e:
            logging.error(f"FanControl: Error during initialization: {e}")

    def on_unload(self, ui):
        logging.info("FanControl: Unloading plugin")
        self.running = False
        if self.pi:
            self.pi.set_PWM_dutycycle(self.FAN_GPIO, 0)  # Turn off fan on exit
            self.pi.stop()
        with ui._lock:
            ui.remove_element("fan_speed")
            ui.remove_element("fan_rpm")
        logging.info("FanControl: Plugin unloaded")

    def on_ui_setup(self, ui):
        logging.info("FanControl: Setting up UI elements")
        ui.add_element("fan_speed", LabeledValue(color=BLACK, label="Fan Speed ", value="0%", position=(100, 95)))
        ui.add_element("fan_rpm", LabeledValue(color=BLACK, label="Fan RPM ", value="0", position=(185, 95)))
        logging.info("FanControl: UI elements set up")

    def on_ui_update(self, ui):
        logging.info("FanControl: Updating UI")
        with ui._lock:
            ui.set("fan_speed", f"{self.fan_speed / 2.55:.0f}% ")
            ui.set("fan_rpm", f"{self.rpm:.0f} ")
        logging.info("FanControl: UI updated")

    def run(self):
        logging.info("FanControl: Running background process")
        while self.running:
            try:
                cpu_temp_f = self.get_cpu_temp()
                logging.info(f"FanControl: CPU Temp: {cpu_temp_f:.1f}F")
                new_fan_speed = self.adjust_fan_speed(cpu_temp_f)
                if new_fan_speed != self.fan_speed:
                    self.set_fan_speed(new_fan_speed)
                    logging.info(f"FanControl: New fan speed set: {new_fan_speed}")
                logging.info(f"FanControl: Fan Speed: {self.fan_speed / 2.55:.0f}%, Fan RPM: {self.rpm:.0f}")
                time.sleep(10)
            except Exception as e:
                logging.error(f"FanControl: Error in run loop: {e}")
        logging.info("FanControl: Background process stopped")

    def get_cpu_temp(self):
        try:
            res = os.popen('vcgencmd measure_temp').readline()
            temp_c = float(res.replace("temp=", "").replace("'C\n", ""))
            temp_f = temp_c * 9.0 / 5.0 + 32.0  # Convert to Fahrenheit
            return temp_f
        except Exception as e:
            logging.error(f"FanControl: Error getting CPU temperature: {e}")
            return 0.0

    def set_fan_speed(self, speed):
        try:
            self.fan_speed = speed
            if self.pi:
                self.pi.set_PWM_dutycycle(self.FAN_GPIO, speed)
                logging.info(f"FanControl: PWM duty cycle set to {speed}")
        except Exception as e:
            logging.error(f"FanControl: Error setting fan speed: {e}")

    def tach_callback(self, gpio, level, tick):
        try:
            if level == 0:
                self.tick_count += 1
                if self.tick_count == 2:  # Two pulses per revolution
                    dt = pigpio.tickDiff(self.last_tick, tick)
                    self.rpm = 60000000 / dt
                    self.tick_count = 0
                    self.last_tick = tick
                    logging.info(f"FanControl: RPM calculated: {self.rpm}")
        except Exception as e:
            logging.error(f"FanControl: Error in tach callback: {e}")

    def adjust_fan_speed(self, cpu_temp_f):
        if cpu_temp_f < 80:  # Below 80°F
            return 0
        elif cpu_temp_f < 85:  # 80°F to 85°F
            return 64  # ~25% speed
        elif cpu_temp_f < 90:  # 85°F to 90°F
            return 128  # ~50% speed
        elif cpu_temp_f < 95:  # 90°F to 95°F
            return 192  # ~75% speed
        else:  # Above 95°F
            return 255  # Full speed
