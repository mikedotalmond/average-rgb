import cv2
import numpy as np
import time
import random

from threading import Thread

"""  
With any given sequence of frame data, allow you to...
* Track suitable features in an input feed and output data about those features
* Randomly pick new candidate features at a configurable rate
* Limit max features
* Debug draw the outputs
"""
class FeatureTracking:

    frame = None
    last_frame = None

    def __init__(self, max_features=8, process_fps=30, debug_draw=False):
        self.frame = None
        self.max_features = 8
        self.update_delay = 1.0 / process_fps
        self.stopped = False
        self.debug_draw = debug_draw  
        self.debug_display=None

        self.p0 = None 

        # params for ShiTomasi corner detection
        self.feature_params = dict(
            maxCorners = max_features,
            qualityLevel = 0.3,
            minDistance = 4,
            blockSize = 7
        )
        # Parameters for lucas kanade optical flow
        self.lk_params = dict(
            winSize  = (15,15),
            maxLevel = 2,
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )


    #
    def start(self):
        self.stopped = False
        Thread(target=self.process, args=()).start()
        return self
        
    #
    def stop(self):
        self.stopped = True
    

    def set_frame(self, frame):
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.frame is None:
            self.debug_display = np.zeros_like(f)
        else:
            self.last_frame = self.frame.copy()
        
        self.frame = f
    
    #
    def process(self):  
        
        self.last_time = time.time()
        self.features_time = self.last_time
        self.last_point_count = 0

        # we periodically pick new features to track
        self.new_feature_time_min = 3.0
        self.new_feature_time_max = 9.0
        self.next_feature_time = self.get_next_feature_time()

        while not self.stopped:

            if self.frame is None or self.last_frame is None:
                time.sleep(self.update_delay)
                continue

            t1 = time.perf_counter()

            #
            img = self.frame
            img_last = self.last_frame
            
            # pick new features to track
            if self.p0 is None or self.last_point_count == 0 or self.last_time - self.features_time > self.next_feature_time:
                self.p0 = cv2.goodFeaturesToTrack(img, mask = None, **self.feature_params)
                self.next_feature_time = self.get_next_feature_time()
                self.features_time = self.last_time

            # perform optical flow
            if self.p0 is not None:
                p1, st, _ = cv2.calcOpticalFlowPyrLK(img_last, img, self.p0, None, **self.lk_params)
                # Select good points
                if p1 is not None:
                    good_new = p1[st==1]
                    good_old = self.p0[st==1]

                self.last_point_count = len(good_new)
                # print(self.last_point_count)

            #
            # update the previous points
            self.p0 = good_new.reshape(-1,1,2)


            # draw tracked features
            if self.debug_draw:
                self.debug_display = np.zeros_like(img)
                for i,new in enumerate(good_new):
                    a,b = new.ravel()
                    self.debug_display = cv2.circle(self.debug_display, (int(a),int(b)), 2, 255, -1)
                
                cv2.imshow('feature_tracking', cv2.add(img, self.debug_display))
                if cv2.waitKey(1) == ord("q"):
                    self.stopped = True      
        
    
            self.last_time = time.time()
            process_time = time.perf_counter() - t1
            # print(f'feature tracking process_time {process_time}')

            sleep_time = self.update_delay - process_time
            time.sleep(sleep_time if sleep_time > 0 else 0)


    def get_next_feature_time(self):
        t = random.randint(self.new_feature_time_min, self.new_feature_time_max)
        # print("next_feature_time:", t)
        return t
