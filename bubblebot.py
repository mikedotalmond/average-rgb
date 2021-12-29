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
from audio_driver import AudioDriver
from twitch_chat import TwitchChat

import argparse

# if debug mode is enabled we show previews of the input with ROI rectangle, the feature tracking, and dominant colours,
# and also simulates bubble pop and creation events (blank frame) periodically

# example usage:  python .\average-rgb\bubblebot.py -source ./raw/MVI_6153.MOV -debug yes -downscale-amount 16
# example usage:  python .\average-rgb\bubblebot.py -source 0 -debug yes -downscale-amount 8
# example usage:  python .\average-rgb\bubblebot.py -source rtsp://your.stream/here -debug yes -downscale-amount 12

# use `-print-timings yes` to log out timings for DominantColours and FeatureTracking to optimise parameters if needed.
# example usage:  python .\average-rgb\bubblebot.py -source 0 -debug yes -print-timings yes -downscale-amount 4
#

# larger downscale amounts will speed up processing and reduce CPU load .. 
# running on a raspberrypi 3b it is easy to max out the CPU cores and have no spare capacity for sonic-pi to run smoothly

parser = argparse.ArgumentParser(description='BubbleBot configuration')
parser.add_argument('-source', default=0, required=False, help="String location of video file to test with, or integer value of capture device to use.")
parser.add_argument('-downscale-amount', type=int, default=12, required=False, help="Amount the media source is downscaled by before processing.")

parser.add_argument('-debug', type=str, default='yes', choices=['yes','no'], required=False)
parser.add_argument('-print-timings', type=str, default='no', choices=['yes','no'], required=False)
parser.add_argument('-fullscreen', type=str, default='no', choices=['yes','no'], required=False)
args = parser.parse_args()

# globals
# simulate a bubble pop event by returning empty frames during development / debugging
bubble_pop_duration = 4.0
bubble_pop_chance = 0.000#5
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
    print_timings = args.print_timings == 'yes'
    
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
        clusters = 3, 
        process_fps = 1, # video_getter.frame_rate/4, 
        debug = debug,
        print_timings = print_timings
    ).start()
    # 
    feature_tracking = FeatureTracking(
        max_features = 9,
        process_fps = video_getter.frame_rate/2,
        debug = debug,
        print_timings = print_timings
    ).start()

    soundtrack = AudioDriver()
    # soundtrack = AudioDriver(osc_ip="192.168.1.118")

    def on_chat_message(data):
        print("on_chat_message", data)
        # message data is a tuple containing...
        name, text, is_broadcaster, is_mod, is_sub = data
    
    twitch_chat = TwitchChat(channel_name="bubbletelevision", on_message = on_chat_message).start()

    #
    #
    frame_time = 1.0 / video_getter.frame_rate
    print(f'video frame_time: {frame_time}')
    print(f'video frame_rate: {video_getter.frame_rate}')
    print(f'video frame_count: {video_getter.frame_count}') # -1 for live camera

    #
    # display output, mostly for development and debugging
    if debug:
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
            break
        
        # if debug mode is set then we occasionally simulate bubble pop/create events.
        frame = get_frame(video_getter) if debug else video_getter.frame
        if frame is None:
            print("no frame data available")
            break

        # downscale input for processing 
        if downscale_amount is not None:
            h, w, _ = frame.shape
            frame = cv2.resize(frame, (w//downscale_amount, h//downscale_amount), interpolation=cv2.INTER_AREA)
        
        # define region-of-interest for processing
        h, w, _ = frame.shape
        # left,top,right,bottom insets (percentage) to define the region of interest for processing
        roi_ltrb = (0.05, 0.05, 0.05, 0.05)
        roi = [int(w*roi_ltrb[0]), int(w*roi_ltrb[1]), w-int(w*roi_ltrb[2]), h-int(w*roi_ltrb[3])]
        
        # udpate data for pop detection
        rgb_test.set_frame(frame, roi = roi)
        bubble_life = roi_test(rgb_test.roi_test, bubble_life)
        
        # if bubble_life.dead:
            # print("bubble death")
            # bubble_life.delay()

        #
        cropped = frame[roi[1]:roi[3],roi[0]:roi[2]]

        # update data for dominant colour calculations
        dominant_colours.set_frame(cv2.resize(cropped, (16,9), interpolation=cv2.INTER_AREA))
        #
        feature_tracking.set_frame(cropped)

        # soundtrack...
        soundtrack.update(
            popped = bubble_life.dead, 
            dominant_colours = {'colours':dominant_colours.hsv, 'weights':dominant_colours.hist}, 
            tracked_features = {'points':feature_tracking.points_normalised, 'velocities':feature_tracking.velocities}
        )

        # show outputs for debugging
        if debug:
            # draw roi
            cv2.rectangle(frame, (roi[0], roi[1]), (roi[2], roi[3]), (0,255,0), 1)
            # show dominant colours
            if dominant_colours.chart is not None:
                cv2.imshow("dominant_colours", dominant_colours.chart)
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

    # exit
    if video_shower is not None: 
        video_shower.stop()
    video_getter.stop()
    rgb_test.stop()
    dominant_colours.stop()
    feature_tracking.stop()   
    twitch_chat.stop()
    cv2.destroyAllWindows()


def main():
    thread_handler()

if __name__ == "__main__":
    main()
