# Recaptcha v2 solver
A simple program to bypass recaptcha version 2 using audio verification method. <br>
This program only demonstrates how to bypass recaptcha on https://www.google.com/recaptcha/api2/demo<br>

## OS support
1. Windows

## Dependencies
1. selenium
2. pydub
3. speech recognition
4. ffmpeg
5. ffmpy
6. stem

## Usage
from recaptha_solver_v2 import ReCaptchaSolver <br>
or <br>
python recaptha_solver_v2.py <br>

## Common errors
Q1. NameError: name 'sample_audio' is not defined <br>
A1. Try installing ffmpeg manually, http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/<br>
