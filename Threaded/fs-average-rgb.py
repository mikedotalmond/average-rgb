import cv2
import randomname
import datetime
import time
from VideoGet import VideoGet
from VideoShow import VideoShow
from RgbTest import RgbTest
from LifeCycle import LifeCycle

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
