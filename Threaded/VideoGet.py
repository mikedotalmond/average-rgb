from threading import Thread
import numpy as np
import time
import cv2

class VideoGet:

    def __init__(self, src=0, width=1920,height=1080):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.frame_count = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT)) # 0 for live streams, an int for video files
        self.frame_rate = float(self.stream.get(cv2.CAP_PROP_FPS))
        (self.grabbed, self.frame) = self.stream.read()

        if self.grabbed and self.frame_rate > 0:
            self.frame_delay = 1.0 /  self.frame_rate
            self.stopped = False
        else:
            print(f'Unable to start VideoCapture for source:{src}')
            self.stop()

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()        
                time.sleep(self.frame_delay)

    def stop(self):
        self.stopped = True
        self.stream.release()