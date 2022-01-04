from threading import Thread
import numpy as np
import time
import cv2

class VideoGet:

    stream : cv2.VideoCapture = None

    def __init__(self, src=0, width=1920, height=1080, allow_skip_frames=True):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.frame_count = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT)) # 0 for live streams, an int for video files
        self.frame_rate = float(self.stream.get(cv2.CAP_PROP_FPS))
        self.allow_skip_frames = allow_skip_frames

        (self.grabbed, self.frame) = self.stream.read()

        if self.frame_count > 0:
            self.stream.set(cv2.CAP_PROP_POS_FRAMES, 0.0)
            self.current_frame = 0
        else:
            self.frame_fraction = 0

        if self.grabbed and self.frame_rate > 0:
            self.frame_time = 1.0 /  self.frame_rate
            self.stopped = False
        else:
            print(f'Unable to start VideoCapture for source:{src}')
            self.stop()

    def start(self):    
        t = Thread(target=self.get, args=())
        t.daemon = True

        self.start_time = time.time()
        t.start()

        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                t = time.time()

                # if total frames known (eg, not a live stream)
                if self.frame_count > 0:
                    
                    if self.allow_skip_frames:
                        self.current_frame = (t - self.start_time) / self.frame_time
                    else:
                        self.current_frame += 1.0
                    
                    #print(self.current_frame)
                    self.stream.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
               
                # print(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
                (self.grabbed, self.frame) = self.stream.read()     

                dt = time.time() - t
                sleep_time = self.frame_time - dt
                if sleep_time > 0:
                    time.sleep(sleep_time)

    def stop(self):
        self.stopped = True
        self.stream.release()