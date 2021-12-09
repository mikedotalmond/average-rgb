from threading import Thread
import numpy as np
import time
import cv2

class VideoGet:

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.frame_count = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = float(self.stream.get(cv2.CAP_PROP_FPS))
        (self.grabbed, self.frame) = self.stream.read()

        self.frame_delay = 1.0 /  self.frame_rate
        self.stopped = False

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