# average-rgb:
A simple Python script to detect and compare the average RGB value of a defined area from a video file, image sequence or camera.

# Requirements:
OpenCV-Python “pip install opencv-python” 			https://pypi.org/project/opencv-python/

The above will work on most desktop machines, for Raspberry Pi see below.


# Usage:
The variable rgb_test = (0, 0, 0) is the RGB value you want to test for. 

upper_left = (x, y) and bottom_right = (x, y) defines the area you want to test, region of interest “roi”.

roi_test is a boolean that is currently set to check if the RGB test value is greater than the region of interest average RGB value. 

Pressing “q” will quit the script. 


# Raspberry Pi Installation:
The following instructions are to install OpenCV on a new installation of Raspberry Pi OS.

Open a new terminal and enter:

pip3 install --user opencv-python==4.5.3.56

sudo apt-get install libatlas-base-dev

pip3 install --user -U numpy
pip3 install --user -U scikit-learn
pip3 install --user -U python-osc
pip3 install --user -U pytmi
