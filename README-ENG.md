[![Total clone count](https://img.shields.io/badge/dynamic/json?color=green&label=Total%20clones&query=count&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/clones.json&logo=github)](#)[![Unique clone count](https://img.shields.io/badge/dynamic/json?color=blue&label=Unique&query=uniques&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/clones.json)](#)[![Today's clone count](https://img.shields.io/badge/dynamic/json?color=purple&label=Today%27s%20clones&query=clones[0][%27count%27]&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/clones.json)](#)

[![Total view count](https://img.shields.io/badge/dynamic/json?color=yellow&label=Total%20views&query=count&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/views.json&logo=github)](#)[![Unique view count](https://img.shields.io/badge/dynamic/json?color=indigo&label=Unique&query=uniques&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/views.json)](#)[![Today's clone count](https://img.shields.io/badge/dynamic/json?color=orange&label=Today%27s%20views&query=views[0][%27count%27]&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/views.json)](#)

# Fake attendance script for you-know-what
For educational purposes only

# A message, mostly for myself
It is complete (macOS needs corresponding images for several popups). What I have been doing since July 3 is not related to functionality; I was trying to improve code style and teach myself various techniques. But now it is becoming more 'coding to code' instead of 'adding necessary features.' I probably should not focus on this much because there are other things to learn.

If anyone comes across an idea for a new, necessary feature, please let me know.

## Requirements
Windows 10 or higher or macOS Ventura. If you want to use it as is, Windows 11 with default settings in Korean. Otherwise, you might have to capture your own images for PyAutoGUI. See [images](images).

Run below in a Python 3 environment, 3.11.3 recommended.

`pip install -r requirements.txt`

Fill out the template [info_template.py](auto_attendance/info_template.py) with your login, email information, and the zoom link _with_ the `#success`. Rename the file to `info.py`

Note: If the module fails to download the Chrome extension source, you can try downloading it manually. Check that its name is `extension_0_1_2_0.crx`, and put it in the root of the repository. See [this](https://crx-downloader.com/how-it-works) for direction. Screen QR Reader url: https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln

Also note for mac users: You may need to grant permission to the terminal access to System Events and Zoom. Go to `System Settings - Privacy & Security - Automation` and give it access to them.

## Run
Run `python -m auto_attendance` for download, Zoom launch, and check-in. Read [How it works and why](#how-it-works-and-why) for explanation.

To change the QR checking schedule, you can add an argument as either:
- `-p` optional argument; one of `'regular'`, `'sprint challenge'`, `'project day 1'`, `'project days 2-5'`, `'section review day 1'`, `'section review day 2'`, and `'project section'` (See [settings.py](auto_attendance/settings.py) for actual timings.)
- `-t` optional argument; a text file that contains a 24-hour format time sets, such as [test_times.txt](test_times.txt)
- or positional argument; a series of time sets, such as `10:00 15:00` (This case would be multiple arguments).

Leaving it blank is the same as `'regular'` argument.

Type `python -m auto_attendance -h` for more information. Note that arguments are parsed in the listed order above, ignoring others when passed correctly.

For a single test to fire right away, run `python -m auto_attendance.fake_check_in`.

Currently supports `Ctrl + Alt(command) + Shift + L` for launching Zoom, `Ctrl + Alt(command) + Shift + C` for checking in with QR code, and `Ctrl + Alt(command) + Shift + Q` for quitting Zoom. These commands work anywhere (inside and outside of the terminal).

## Quit
To quit, press `Ctrl + C` in the terminal or `Ctrl + Alt(command) + Shift + E` anywhere. The former is the default hotkey for quitting a Python script, and the latter is a user-defined hotkey: see [scheduler.py](https://github.com/yjmd2222/fake-attendance/blob/d38ceb32321eac70bbd7902cd87dd7bd88a61a6d/auto_attendance/scheduler.py#L124-L127) and [settings.py](https://github.com/yjmd2222/fake-attendance/blob/d38ceb32321eac70bbd7902cd87dd7bd88a61a6d/auto_attendance/settings.py#L111).

The second hotkey allows quitting even when not focused on the terminal, and it may not work in the middle of a job until the job is finished which I believe is due to the usage of `APScheduler`'s `BackgroundScheduler`.

## How it works and why
[![Last updated](https://img.shields.io/badge/Last_updated-2023--06--21-blue)](#)

This module automates all check-ins for you-know-what: launch and quit Zoom at corresponding times and read the QR code in Zoom to complete the check-in form.
This check is done throughout the day. See [settings.py](auto_attendance/settings.py) for the actual timings.

So why this? My online class used to require I sit at the desk on Zoom from 9 AM to 6 PM (lunch time from 12 to 1 is excluded) with camera on the entire time.
This is ridiculous, and everyone must be thinking of putting on a fake recording of themself in the background. But the admins are going to send a QR image for us to check in every hour or two
which is on another level of shit. So I made a little script that scans the QR image on the Zoom meeting. They said they would give 10 minutes to check in,
so the script checks multiple times around the check-in time.

But then they changed the rules to allow turning off the Zoom camera, so this part is removed. You can look at the archived code in [turn_on_video.py](archive/turn_on_video.py)

The other day I learned Selenium and its RPA and APIs, so this is a little project of what I learned. The admins must be happy.

This is all a joke :) Interpreting what I mean with 'this' is up to you, as in the whole script or the whole situation.

## Credits
- You-know-what admins and the overseers and their disrespect for privacy that gave me the idea for this project
- tkobayashi0111 for [Screen QR Reader](https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln)
- Yay me for starting and maintaining this project

## License
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This work is licensed under the Apache 2.0 License.
