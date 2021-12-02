import cv2
 
vid = cv2.VideoCapture(0) # define a video capture object
 
rgb_test = (20, 20 , 20) #RGB values to test against 
upper_left = (240, 180) #Region of intrest (x1, y1)
bottom_right = (400, 300) #Region of intrest (x2, y2)
 
while(True): 
    ret, frame = vid.read() # Capture the video frame 
    rect_img = frame[upper_left[1] : bottom_right[1], upper_left[0] : bottom_right[0]] # Region of intrest = image[y1:y2, x1:x2]
    cv2.rectangle(frame, (upper_left[0], upper_left[1]), (bottom_right[0], bottom_right[1]), (0,255,0), 1) #Draw rectangle of region of intrest
    cv2.imshow("Bubble Test", frame)    # Display the resulting frame, this can be commented out. Only for visual feeback
    roi_mean = cv2.mean(rect_img) #Mean RGB values of region of intrest
    roi_test = all(x > y for x, y in zip(rgb_test, roi_mean)) #Test the region of intrest vs test RGB value
    if roi_test: 
        print("Do servo stuff here")
    else:
        print("Bubble still visible")
 
    if cv2.waitKey(1) & 0xFF == ord('q'): #Press q to quit 
        break
 
vid.release() # After the loop release the cap object 
 
cv2.destroyAllWindows() # Destroy all the windows
