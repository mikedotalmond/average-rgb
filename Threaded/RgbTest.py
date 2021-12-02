from threading import Thread
import time
import cv2

class RgbTest:

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False
        self.rgb_test= (15, 15 , 15) #RGB values to test against 
        self.upper_left = (20, 20) #Region of intrest (x1, y1)
        self.bottom_right = (1900, 1060) #Region of intrest (x2, y2)
        self.roi_test = False
        

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            rect_img = self.frame[self.upper_left[1] : self.bottom_right[1], self.upper_left[0] : self.bottom_right[0]] 
            roi_mean = cv2.mean(rect_img) #Mean RGB values of region of intrest
            self.roi_test = all(x > y for x, y in zip(self.rgb_test, roi_mean)) #Test the region of intrest vs test RGB value
           #cv2.rectangle(self.frame, (self.upper_left[0], self.upper_left[1]), (self.bottom_right[0], self.bottom_right[1]), (0,255,0), 1)
            time.sleep(0.01)

    def stop(self):
        self.stopped = True