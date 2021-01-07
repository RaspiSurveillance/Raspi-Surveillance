# Raspi-Surveillance

Raspberry Pi Home Surveillance.

Sends messages and takes and sends photos on motion detected.

* Messages via Telegram and/or Mail
* Taken photos via Telegram and/or Dropbox

## Copyright

(C) 2019-2021 Denis Meyer

## Prerequisites

### Hardware

* Motion detector (infrared sensor)
* Camera

For hardware details check out "plans".

### Software

* A set up Raspberry Pi (For details check out "plans")
* Python 3 (as "python3")
* MP4Box for video processing
  * sudo apt-get install gpac
* Windows
  * Add Python to PATH variable in environment
* Configure settings.json

## Usage

* Configure src/settings.json

* Start shell
* Install the required libraries
  * Install pigpiod (has to be runnable via `sudo pigpiod`)
  * `pip install -r requirements.txt`
* Run the app via script
  * `./scripts/start.sh`
  * Stop the app via script
    * `./scripts/stop.sh`
* Run the app
  * `cd src`
  * `python raspi-surveillance.py`
  * Stop the app
    * Ctrl-C

## About

### Workflow

1. Checks for infrared sensor data (loop)
2. If motion is detected (and has not been detected for $sleep.check_sensors_sec seconds):
    * Takes images and video
    * Sends message that motion has been detected to all "Senders" (see more at chapter "Senders")
    * After finished taking images, uploads the images to all "Senders"

### Senders

Senders are channels that can be asked to send messages and images (if they support them).

#### Log Sender

* Logs message details
* Logs image details
* Logs video details

#### Mail Sender

* Sends messages
* Does not support images
* Does not support videos

#### Dropbox Sender

* Does not support messages
* Sends images
* Sends videos

#### Telegram Sender

* Sends messages
* Sends images
* Sends videos
