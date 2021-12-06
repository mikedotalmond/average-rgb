from threading import Thread
import time
import cv2

class RgbTest:

    def __init__(self, frame=None, process_fps=8):
        self.set_frame(frame, roi=[0, 0, 32, 32])
        self.stopped = False
        self.rgb_test= (15, 15 , 15) #RGB values to test against 
        self.roi_test = False
        self.update_delay = 1.0 / process_fps
        
    def set_frame(self, frame, roi):
        self.frame = frame
        self.roi = roi

    def start(self):
        self.stopped = False
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            rect_img = self.frame[self.roi[0] : self.roi[2], self.roi[1] : self.roi[3]] 
            roi_mean = cv2.mean(rect_img) #Mean RGB values of region of interest
            self.roi_test = all(x > y for x, y in zip(self.rgb_test, roi_mean)) #Test the region of interest vs test RGB value
            time.sleep(self.update_delay)

    def stop(self):
        self.stopped = True