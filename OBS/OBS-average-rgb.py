import cv2 
import datetime
from obswebsocket import obsws, requests 
import randomname
 
host = "localhost" #IP of computer running OBS
port = 4444
password = "password"
 
vid = cv2.VideoCapture(0) # define a video capture object

rgb_test= (15, 15, 15) #RGB values to test against 
upper_left = (40, 40) #Region of intrest (x1, y1)(240, 180)
bottom_right = (600, 440) #Region of intrest (x2, y2)(400, 300)

ws = obsws(host, port, password)
ws.connect()
source_vis = True 

while(True): 
 
    ret, frame = vid.read() # Capture the video frame 
 
    rect_roi = frame[upper_left[1] : bottom_right[1], upper_left[0] : bottom_right[0]] # Region of intrest = image[y1:y2, x1:x2]
    cv2.rectangle(frame, (upper_left[0], upper_left[1]), (bottom_right[0], bottom_right[1]), (0,255,0), 1) #Draw rectangle of region of intrest
    cv2.imshow('Bubble Test', frame)    # Display the resulting frame, this can be commented out. Only for visual feeback
 
    roi_mean = cv2.mean(rect_roi) #Mean RGB values of region of intrest
 
    roi_test = all(x > y for x, y in zip(rgb_test, roi_mean)) #Test the region of intrest vs test RGB value
    if roi_test: 
        if not source_vis:
            print("Change Source Vis to ON")
            ws.call(requests.SetSceneItemRender("bubble_image", True))
            source_vis = True
            age = datetime.datetime.now() - born_dt
            print (name + " Died " + datetime.datetime.now().strftime("%d.%m.%Y At %H:%M:%S"))
            minutes = divmod(age.seconds, 60) 
            if minutes[0] == 0:
                print("Aged", minutes[1], 'seconds')
            else:
                print("Aged", minutes[0], 'minutes',minutes[1], 'seconds')
            #print("Do servo stuff here")
    else:
        if source_vis:
            print("Change Source Vis to OFF")
            ws.call(requests.SetSceneItemRender("bubble_image", False))
            source_vis = False
            name = randomname.get_name()
            name = name.replace("-", " ")
            name = name.title()
            born_dt = datetime.datetime.now()
            print (name + " Born " + born_dt.strftime("%d.%m.%Y At %H:%M:%S"))
            #print("Bubble still visible")
 
    if cv2.waitKey(1) & 0xFF == ord('q'): #Press q to quit 
 
        break
 
ws.disconnect()
 
vid.release() # After the loop release the cap object 
 
cv2.destroyAllWindows() # Destroy all the windows