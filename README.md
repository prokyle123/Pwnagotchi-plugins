### FanControl Plugin for Pwnagotchi

This plugin allows you to control a PWM fan based on the CPU temperature of your Pwnagotchi device. It dynamically adjusts the fan speed to keep the CPU within optimal operating temperatures, providing more granular control with 40 different fan speed increments between 70°F and 140°F. The plugin also displays the current fan speed and RPM on the Pwnagotchi's display.

### Features

- Adjusts fan speed based on CPU temperature in 40 increments for granular control.
- Displays current fan speed as a percentage and RPM on the Pwnagotchi screen.
- Automatically starts and stops the fan based on temperature thresholds.
- Toggleable in web plugins web UI

### Requirements

- Pwnagotchi device with a compatible PWM fan connected to GPIO18 and a tachometer connected to GPIO23.
- pigpio library installed and running.

### Installation Instructions

1. **Install pigpio Library**:
   Ensure the pigpio library is installed on your Pwnagotchi device.
   ```bash
   sudo apt-get update
   sudo apt-get install pigpio python3-pigpio

Start pigpio Daemon:
Start the pigpio daemon to control the GPIO pins.

sudo systemctl start pigpiod
sudo systemctl enable pigpiod

Download and Install FanControl Plugin:
Clone the repository and place the fan_control.py file in your custom plugins directory.

****************DOWNLOAD FROM HERE IF YOUV MADE IT THIS FAR *******************************

cd fan_control

sudo cp fan_control.py /usr/local/share/pwnagotchi/custom-plugins/

**********************************Edit Pwnagotchi Configuration:*************************************
Enable the FanControl plugin in your Pwnagotchi configuration file.

sudo nano /etc/pwnagotchi/config.toml

main.plugins.fan_control.enable = true


Usage
Once installed and configured, the FanControl plugin will automatically adjust the fan speed based on the CPU temperature and display the fan speed and RPM on the Pwnagotchi screen.

******************************Troubleshooting*****************************************
Fan Not Spinning: Ensure the pigpio daemon is running and that the GPIO pins are correctly configured.
Incorrect Temperature Readings: Verify that the vcgencmd tool is installed and functioning correctly.
