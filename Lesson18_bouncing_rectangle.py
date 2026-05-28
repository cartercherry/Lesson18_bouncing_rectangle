##########################################################################################
#  Lesson 18: bounce rectangle(s) off the 4 borders of the video window                  #
#  a sound is played when the rectangles hit a  wall of the window                      #
#  Insure the rectrangles do not go past the 4 walls of the container                    #
##########################################################################################

import cv2
from picamera2 import Picamera2
import time
import subprocess    # to run the sound effects with aplay built into Bookworm OS

W = 1280    #container width 
H = 640     # container height
CAMv3 = 1    # module 3 rpi cam
CAMv2_1 = 0  # rpi cam v2.1
window_moved = False
x0_r = int(.02*W)   #L upper x and y for fps rectangle
y0_r = int(.02*H)   
x1_r = int(.15*W)   # R lower x and y for fps rectangle
y1_r = int(.11*H)     
r_color = (0,0,255)      #fps rectangle color
r_text_color = (0,0,0)   # fps text color
fps_filtered = 0         # low pass filter for fps
font = cv2.FONT_HERSHEY_PLAIN  
textLowerLeft = (int(.025*W), int(.08*H))  # fps text location within fps rectangle

#set up parameters for two moving rectangles, moving independently
xV = 10    # x velocity rectangle 1
yV = 15    #y velocity  rectangle 1 
x2V = 15   #x2 velocity rectangle 2
y2V = 10   #y2 velocity rectangle 2
xD = 1     # x direction rectangle 1
yD = 1     # y direction  rectangle 1
x2D = -1   # x2 direction rectangle 2
y2D =  -1  # y2 direction rectangle 2 
xPos = 200 # L upper corner rectangle 1
yPos = 200 # L upper corner rectangle 1
x2Pos = 400  # L upper corner rectangle 2
y2Pos = 400  # L upper corner rectangle 2
rW = 100  # rectangle 1 Width
rH = 50   # rectangle 1 Height
r2W = 75  #rect 2 width
r2H = 50  #rect 2 height

def init_camera(cam, width, height):
    piCam = Picamera2(cam)   # 1 = module 3 cam;   0 = v2.1 cam 
    W = width                #1280
    H = height               #640
    RES = (W,H)              #resolution
    piCam.preview_configuration.main.size = RES
    piCam.preview_configuration.main.format = "RGB888"
    piCam.preview_configuration.main.align()
    piCam.configure("preview")
    piCam.start()  
    return piCam

piCam = init_camera(CAMv3,W,H)      
cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
try:
    while True:
        time_stamp = time.time()
        frame = piCam.capture_array()  
        frame = cv2.flip(frame, -1)
        cv2.rectangle(frame,(x0_r,y0_r),(x1_r,y1_r),r_color,-1)  # fps rectangle
        xPos = xPos+(xV* xD)  # rectangle 1
        yPos = yPos+(yV* yD) 
        x2Pos = x2Pos + (x2V * x2D )  # move rectangle 2
        y2Pos = y2Pos + (y2V * y2D) 
        if (xPos <0) or (xPos + rW) > W:  # check for L,R wall crashes with rectangle 1
            subprocess.Popen(['aplay','crash.wav'])
            xD = -xD
            xPos = xPos+(xV * xD )  # updated rectangle 1 movement
        if (x2Pos <0) or (x2Pos + r2W) > W:  # check for L,R wall crashes rectangle 2
            subprocess.Popen(['aplay','boom.wav'])
            x2D = -x2D  # crash, change direction
            x2Pos = x2Pos+(x2V * x2D )  # updated rectangle 2 movement

        if (yPos <0) or (yPos + rH) > H:  #check for upper and lower wall crashes rectangle 1
            subprocess.Popen(['aplay','crash.wav'])
            yD = -yD  # crash detected, change direction
            yPos =yPos+(yV* yD)  # new movement after crash
        if (y2Pos <0) or (y2Pos + r2H) > H: # check for upper and lower wall crashes rectangle 2
            subprocess.Popen(['aplay','boom.wav'])
            y2D = -y2D
            y2Pos =y2Pos+(y2V* y2D)

        cv2.rectangle(frame,(xPos, yPos),(xPos+rW,yPos+rH),(255,0,0),-1)  #initialize rectangle 1
        cv2.rectangle(frame,(x2Pos, y2Pos),(x2Pos+r2W,y2Pos+r2H),(0,255,0),-1)  # initialize rectangle 2
        key= cv2.waitKey(1) & 0xff
        if not window_moved:
            cv2.moveWindow('Video', 0, 50)
            cv2.resizeWindow("Video",W,H)
            window_moved = True
        if key == ord('q'):
            print("Quit signal received.")
            break
        dt = time.time() - time_stamp
        fps = 1/dt
        fps_filtered = .95*fps_filtered + .05*fps
        cv2.putText(frame,f'{fps_filtered:0.1f} FPS',textLowerLeft,font,.0012*W,r_text_color,int(.001563*W) ) 
        cv2.imshow("Video",frame)
except KeyboardInterrupt:
    cv2.destroyAllWindows()  #clean up and terminate
    piCam.stop()
    print("program terminated")
