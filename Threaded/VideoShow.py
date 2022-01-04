from threading import Thread
import time
import cv2

class VideoShow:

    def __init__(self, frame=None, fullscreen=True, framerate=30):
        self.frame = frame
        self.stopped = False
        self.fullscreen = fullscreen
        self.frame_delay = 1.0 / framerate

    def start(self):
        t = Thread(target=self.show, args=())
        t.daemon = True
        t.start()
        return self

    def show(self):
        while not self.stopped:
            window_name = 'Bubble Test'
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN if self.fullscreen else None)
            if self.fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            cv2.imshow(window_name, self.frame)

            if cv2.waitKey(1) == ord("q"):
                self.stopped = True
                
            time.sleep(self.frame_delay-0.001)

    def stop(self):
        self.stopped = True