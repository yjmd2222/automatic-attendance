# Fake attendance script for you-know-what
For educational purposes only

# Requirements
Any OS should work, but only tested on Windows 11

Run below in a Python 3 environment, 3.11.3 recommended.

`pip install -r requirements.txt`

Install the Chrome extension [Screen QR Reader](https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln).

Install Zoom.

Fill out the template `info-template.py` with your Gmail information or modify to match your email provider configuration. Rename the file to `info.py`

Enter a Zoom conference.

# Run
`python main.py`

# How it works and why
The script assumes a Zoom meeting is live and checks if there is a QR image on the meeting screen. Screen QR Reader scans the QR image, and the output link is copied. The link is sent to the email provided (The sender and the receiver are the same). This is done every five minutes.

My online class requires I sit at the desk on Zoom from 9 AM to 6 PM (lunch time from 12 to 1 is excluded) with camera on the entire time. This is ridiculous, and everyone must be thinking of putting on a fake recording of themself in the background. But the admins are going to send a QR image for us to check in every hour or two which is on another level of shit. So I made a little script that scans the QR image on the Zoom meeting. They said they would give 10 minutes to check in, so the script checks every five minutes, but that may change, not so hard.

The other day I learned Selenium and its RPA and APIs, so this is a little project of what I learned. The admins must be happy.

This is all a joke :) Interpreting what I mean with 'this' is up to you, as in the whole script or the whole situation.

# Credits
- You-know-what admins and the overseers and their disrespect for privacy that gave me the idea for the script
- tkobayashi0111 for [Screen QR Reader](https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln)
- yay me for this script