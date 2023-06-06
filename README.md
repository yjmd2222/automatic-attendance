# Fake attendance script for you-know-what
For educational purposes only

## Requirements
Windows 10 or higher. If you want to use it as is, Windows 11 with default settings in Korean.

Run below in a Python 3 environment, 3.11.3 recommended.

`pip install -r requirements.txt`

Install the Chrome extension [Screen QR Reader](https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln).

Fill out the template `info-template.py` with your Gmail information or modify to match your email provider configuration. Rename the file to `info.py`

Enter a Zoom conference.

Customizing search images is most likely required for your own PC: Replace the images with those found on your screen. `win + shift + s` is a shortcut that allows you to capture a portion of the screen.

## Run
`python main.py`

## How it works and why
The script assumes a Zoom meeting is live and checks if there is a QR image on the meeting screen. Screen QR Reader scans the QR image, and the output link is copied.
The link is sent to the email provided (The sender and the receiver are the same). This is done every seven minutes.

Along with that, it also turns on Zoom Video on 1 PM, so make sure you have a recording of yourself pre-selected as the background.
You may also need to look for a virtual camera so that the actual webcam feeds video into it on your command. A virtual camera without live video feed from the webcam works as a blackscreen,
so you can only see the background image (video recording) that you chose in Zoom settings. Switch on and off the webcam feed and the background image (video), so there is only one of you, not two.

You may also want to look into how to run two instances of Zoom. This is to record yourself in the morning and use it in the afternoon. Same background and resolution.

So why this? My online class requires I sit at the desk on Zoom from 9 AM to 6 PM (lunch time from 12 to 1 is excluded) with camera on the entire time.
This is ridiculous, and everyone must be thinking of putting on a fake recording of themself in the background. But the admins are going to send a QR image for us to check in every hour or two
which is on another level of shit. So I made a little script that scans the QR image on the Zoom meeting. They said they would give 10 minutes to check in,
so the script checks every seven minutes, but that may change, not so hard.

The other day I learned Selenium and its RPA and APIs, so this is a little project of what I learned. The admins must be happy.

This is all a joke :) Interpreting what I mean with 'this' is up to you, as in the whole script or the whole situation.

## Credits
- You-know-what admins and the overseers and their disrespect for privacy that gave me the idea for the script
- tkobayashi0111 for [Screen QR Reader](https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln)
- yay me for this script

## License
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This work is licensed under the Apache 2.0 License.
