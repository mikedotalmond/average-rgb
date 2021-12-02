import cv2
import randomname
import datetime
import time
from VideoGet import VideoGet
from VideoShow import VideoShow
from RgbTest import RgbTest

class LifeCycle: 
    def __init__(self):
        self.first_run = True
        self.name = ""
        self.born_dt = None
        self.born_text = ""
        self.death_text = ""
        self.age = ""
        self.dead = False
    
    def delay(self):
        time.sleep(5)

    def born(self):
        self.dead = False
        self.death_text = ""
        self.age = ""
        self.name = randomname.get_name()
        self.name = self.name.replace("-", " ")
        self.name = self.name.title()
        self.born_dt = datetime.datetime.now()
        self.born_text =  self.name + " Born " + self.born_dt.strftime("%d.%m.%Y At %H:%M:%S")

    def death(self):
        self.dead = True
        self.age = datetime.datetime.now() - self.born_dt
        minutes = divmod(self.age.seconds, 60) 
        self.death_text = "Died " + datetime.datetime.now().strftime("%d.%m.%Y At %H:%M:%S")
        if minutes[0] == 0:
            self.age ="Aged " + str(minutes[1]) + " seconds"
        elif minutes[0] == 1:
            self.age = "Aged " + str(minutes[0]) + " minute " + str(minutes[1]) + " seconds"
        else:
            self.age = "Aged " + str(minutes[0]) + " minutes " + str(minutes[1]) +" seconds"


def roi_test(roi_test, bubble):
    if roi_test:
        #print("Do servo stuff here")
        if not bubble.first_run:
            bubble.first_run = True
            bubble.death()
            return bubble
        return bubble
    else:
        #print("Bubble still visible")
        if bubble.first_run:
            bubble.first_run = False
            bubble.born()
            return bubble
        return bubble
 
def draw_text(frame, bubble_life):
    cv2.putText(frame, bubble_life.born_text,
                (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255))
    cv2.putText(frame, bubble_life.death_text,
                (10, 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255))
    cv2.putText(frame, bubble_life.age,
                (10, 90), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255))


def thread_handler(source=0):
    video_getter = VideoGet(source).start()
    video_shower = VideoShow(video_getter.frame).start()
    rgb_test = RgbTest(video_getter.frame).start()
    bubble_life = LifeCycle()

    while True:
        if video_getter.stopped or video_shower.stopped:
            video_shower.stop()
            video_getter.stop()
            rgb_test.stop()
            break

        frame = video_getter.frame
        rgb_test.frame = frame
        bubble_life = roi_test(rgb_test.roi_test, bubble_life)
        draw_text(frame, bubble_life)
        if bubble_life.dead:
            bubble_life.delay()
        video_shower.frame = frame

def main():
    thread_handler(0)

if __name__ == "__main__":
    main()
