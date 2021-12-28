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
    points = None
    velocities = None
    points_normalised=None

    def __init__(self, max_features=8, process_fps=30, debug=False, print_timings=False):
        self.frame = None
        self.max_features = max_features
        self.update_delay = 1.0 / process_fps
        self.stopped = False
        self.debug = debug  
        self.print_timings = print_timings
        self.debug_display=None
        self.points=[]
        self.velocities=[]
        self.points_normalised=[]
        self.width=1
        self.height=1
        self.half_width=0.5
        self.half_height=0.5

        self.p0 = None

    #
    def init_frame(self, frame):

        if self.debug:
            self.debug_display = np.zeros_like(frame)
        
        h, w = frame.shape
        self.width=w
        self.height=h
        self.half_width=w/2.0
        self.half_height=h/2.0

        print("init frame")
        print(w,h)

        # params for ShiTomasi corner detection
        self.feature_params = dict(
            maxCorners = self.max_features,
            qualityLevel = 0.2,
            minDistance = w//9,
            blockSize = w//27
        )
        # Parameters for lucas kanade optical flow
        self.lk_params = dict(
            winSize  = (15,15),
            maxLevel = 2,
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )

        self.last_frame_time = 0

    #
    def start(self):
        self.stopped = False
        t = Thread(target=self.process, args=())
        t.daemon = True
        t.start()
        return self
        
    #
    def stop(self):
        self.stopped = True
    

    def set_frame(self, frame):
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.frame is None:
            self.init_frame(f)
        else:
            self.last_frame = self.frame.copy()
        
        self.frame = f
    
    #
    def process(self):  
        
        self.last_time = time.time()
        self.features_time = self.last_time
        self.last_point_count = 0

        # we periodically pick new features to track
        self.new_feature_time_min = 1.0
        self.new_feature_time_max = 5.0
        self.next_feature_time = self.get_next_feature_time()

        while not self.stopped:

            if self.frame is None or self.last_frame is None:
                time.sleep(self.update_delay)
                continue

            t1 = time.perf_counter()
            dt = t1 - self.last_frame_time
            self.last_frame_time = t1

            #
            img = self.frame
            img_last = self.last_frame
            
            good_new = None
            good_old = None
            new_features = False

            # pick new features to track
            if self.p0 is None or self.last_point_count == 0 or self.last_time - self.features_time > self.next_feature_time:
                new_features = True
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
                    
                    if not new_features:
                        w2 = self.half_width
                        h2 = self.half_height

                        self.points = good_new

                        # distance moved / time - normalised
                        self.velocities = ((good_new - good_old) / dt) / w2

                        # remap points between -1/1 with 0,0 at the image centre
                        self.points_normalised = [ ([pt[0] / w2 - 1.0, pt[1] / h2 - 1.0]) for pt in good_new ]

                    self.last_point_count = len(good_new)
            #
            # update the previous points
            if good_new is not None:
                self.p0 = good_new.reshape(-1,1,2)
          
                # draw tracked features
                if self.debug:
                    self.debug_display = np.zeros_like(img)
                    for i,(new,old) in enumerate(zip(good_new, good_old)):
                        a,b = new.ravel()
                        c,d = old.ravel()
                        self.debug_display = cv2.circle(self.debug_display, (int(a),int(b)), 2, 255, -1)
                    
                    cv2.imshow('feature_tracking', cv2.add(img, self.debug_display))
                    if cv2.waitKey(1) == ord("q"):
                        self.stopped = True
            
            self.last_time = time.time()
            process_time = time.perf_counter() - t1
            if self.print_timings:
                print(f'feature_tracking process_time {process_time}')
            
            sleep_time = self.update_delay - process_time
            time.sleep(sleep_time if sleep_time > 0 else 0)


    def get_next_feature_time(self):
        return random.randint(self.new_feature_time_min, self.new_feature_time_max)

