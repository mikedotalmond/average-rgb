import cv2
import time

import numpy as np
import random

from Threaded.VideoGet import VideoGet
from Threaded.VideoShow import VideoShow
from Threaded.RgbTest import RgbTest
from Threaded.LifeCycle import LifeCycle

from dominant_colours import DominantColours
from feature_tracking import FeatureTracking

# quick OSC test...
# from pythonosc import osc_message_builder
# from pythonosc import udp_client
# sender = udp_client.SimpleUDPClient('127.0.0.1', 4560)
# sender.send_message('/trigger/test', [50, 100, 1])

# required libs... 
# scikit-learn
# opencv-python
# python-osc

# 
# example use:
# python .\average-rgb\bubblebot.py -source 0 -debug yes -downscale-amount 8
# python .\average-rgb\bubblebot.py -source ./raw/MVI_6151.MOV -downscale-amount 12 -debug yes


import argparse

parser = argparse.ArgumentParser(description='BubbleBot configuration')
parser.add_argument('-source', default=0, required=False, help="String location of video file to test with, or integer value of capture device to use.")
parser.add_argument('-downscale-amount', type=int, default=4, required=False, help="Amount the media source is downscaled by before processing.")
parser.add_argument('-debug', type=str, default='yes', choices=['yes','no'], required=False)
parser.add_argument('-display-output', type=str, default='yes', choices=['yes','no'], required=False)
parser.add_argument('-fullscreen', type=str, default='no', choices=['yes','no'], required=False)
args = parser.parse_args()

# globals
# simulate a bubble pop event by returning empty frames during development / debugging
bubble_pop_duration = 2.0
bubble_pop_chance = 0.001
showing_empty_frame_time = -1.0
showing_empty_frame = False
empty_frame = np.zeros((1080, 1920, 3), np.uint8)

#
#  debug mode get_frame - provide a way to simulate bubble pop/create events 
def get_frame(video_getter):

    global bubble_pop_chance
    global bubble_pop_duration
    global showing_empty_frame
    global showing_empty_frame_time
    global empty_frame

    if showing_empty_frame:
        if (time.time() - showing_empty_frame_time) > bubble_pop_duration:
            print("PING! Simulated new bubble occurred...")
            showing_empty_frame = False
        return empty_frame 

    if random.random() < bubble_pop_chance:
        print("POP! Simulated bubble-pop occurred...")
        showing_empty_frame = True
        showing_empty_frame_time = time.time()
        return empty_frame

    return video_getter.frame


#
## respond to bubble pop detection 
def roi_test(roi_test, bubble):
    if roi_test:
        # print("bubble pop! Do servo stuff here")
        if not bubble.first_run:
            bubble.first_run = True
            bubble.death()
            return bubble
    else:
        # print("Bubble still visible")
        if bubble.first_run:
            bubble.first_run = False
            bubble.born()
    return bubble
    

# video source can be integer or string to a local video file
# so parse string input from args to an integer if needed
def parse_source(s):
    try:
        value = int(s)
        return value
    except ValueError:
        return s

#
#
def thread_handler():

    source = parse_source(args.source)
    downscale_amount = int(args.downscale_amount) 
    fullscreen = args.fullscreen == 'yes'
    debug = args.debug == 'yes'
    display_output = args.display_output == 'yes'
    
    # video stream provider
    video_getter = VideoGet(source).start()

    # pop detection
    rgb_test = RgbTest(
        video_getter.frame, 
        process_fps = 8
    ).start()
    #
    bubble_life = LifeCycle()

    #
    # dominant colours
    dominant_colours = DominantColours(
        clusters = 5, 
        process_fps = video_getter.frame_rate/4, 
        draw_chart = debug
    ).start()
    # 
    feature_tracking = FeatureTracking(
        max_features = 13,
        process_fps = video_getter.frame_rate,
        debug_draw = debug
    ).start()

    #
    #
    frame_time = 1.0 / video_getter.frame_rate
    print(f'video frame_time: {frame_time}')
    print(f'video frame_rate: {video_getter.frame_rate}')
    print(f'video frame_count: {video_getter.frame_count}') # -1 for live camera

    #
    # display output, mostly for development and debugging
    if display_output:
        video_shower = VideoShow(video_getter.frame, fullscreen).start()
    else:
        video_shower = None

    current_frame = 0

    #
    # main loop
    while True:
        t1 = time.perf_counter()

        # break if stopped
        if video_getter.stopped or dominant_colours.stopped or feature_tracking.stopped or (video_shower is not None and video_shower.stopped):
            if video_shower is not None: 
                video_shower.stop()
            video_getter.stop()
            rgb_test.stop()
            dominant_colours.stop()
            feature_tracking.stop()
            break
        
        # if debug mode is set then we occasionally simulate bubble pop/create events.
        frame = get_frame(video_getter) if debug else video_getter.frame

        # downscale input for processing 
        if downscale_amount is not None:
            h, w, _ = frame.shape
            frame = cv2.resize(frame, (w//downscale_amount, h//downscale_amount))
        
        # define region-of-interest for processing
        h, w, _ = frame.shape
        roi = [w//28, w//28, w-w//28, h-w//28]
        
        # udpate data for pop detection
        rgb_test.set_frame(frame, roi = roi)
        bubble_life = roi_test(rgb_test.roi_test, bubble_life)
        
        # if bubble_life.dead:
            # print("bubble death")
            # bubble_life.delay()

        cropped = frame[roi[1]:roi[3], roi[0]:roi[2]]

        # update data for dominant colour calculations
        dominant_colours.set_frame(cv2.resize(cropped, (h//64, w//64)))
        #
        feature_tracking.set_frame(cropped)


        # show outputs for debugging
        if debug and display_output:
            # draw roi
            cv2.rectangle(frame, (roi[0], roi[1]), (roi[2], roi[3]), (0,255,0), 1)
            # show dominant colours
            if dominant_colours.chart is not None:
                cv2.imshow("dominant_colours", dominant_colours.chart)
                # cv2.imshow("feature_tracking", feature_tracking.chart)
                if cv2.waitKey(1) == ord("q"):
                    video_getter.stop()
    
            if video_shower is not None: 
                video_shower.frame = frame
        
        #
        current_frame += 1
        # limit to run this loop at framerate of the source media
        process_time = time.perf_counter() - t1
        sleep_time = frame_time - process_time
        time.sleep(sleep_time if sleep_time > 0 else 0)
        

def main():
    thread_handler()

if __name__ == "__main__":
    main()
