########################################################################################
#  Lesson 24: ROI,  AI on the Edge  06/13/26                                           #
#  Capture, using mouse events, a Region of Interest (ROI), then convert the ROI to    #
#            gray scale.  Position both the ROI and ROIgray windows to the right of    #
#            the 'Camera' Window.                                                      #
#            Make ROI mouse selection from L upper corner to R lower corner            #             
#  Lesson 24 reference:  https://www.youtube.com/watch?v=-r_mFPc_G8g                   #
########################################################################################

import cv2
import time
import numpy as np
from picamera2 import Picamera2
import board
import busio
import adafruit_pca9685

MAX_DUTY = 43000   # for pwm, Pca9685 PWM board
drawing_rect = False    # True when L_Button_Down, False when released
rect_corner1 = (None,None)
rect_corner2 = (None,None)


# Setup the PCA9685 PWM board via I2C
def init_PWM():
    print("Initializing I2C and PCA9685...")
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = adafruit_pca9685.PCA9685(i2c)
    pca.frequency = 1000  # 1000Hz is a smooth frequency for LED dimming
    red_led = pca.channels[5]
    green_led = pca.channels[6]
    blue_led = pca.channels[7]
    return red_led,green_led, blue_led

red_led, green_led, blue_led = init_PWM()

W=1280
H=720
TOP_WASTE = 60   #start window this many pixels from the top
WINDOW_WASTE = 90  # wasted space in window above

fps = 0
tStart = time.time()  # fps timer

def init_PiCam():
    global W,H
    piCam = Picamera2(1)  # v3 rpi camera  
    RES = (W,H)
    piCam.preview_configuration.main.size = RES
    piCam.preview_configuration.main.format = "RGB888"
    piCam.preview_configuration.controls.FrameRate=60
    piCam.preview_configuration.align()
    piCam.configure("preview")
    return piCam

piCam = init_PiCam()
piCam.start()

# set up textStrings for FPS, cursor:(x,y), and RGB at (x,y) on frame
textLowerLeft = (int(W*.01),int(H*.06))  # fps
textLowerLeft1 = (int(W*.01),int(H*.06)*2)  # (x,y)
textLowerLeft2 = (int(W*.01),int(H*.06)*3)   # RGB
fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontThickness = int(W/625)    #425 drfault  DEBUG
fontScale = H*.0015
fontColor = (0,0,255)
xPos, yPos = 0,0
valR, valG, valB = 0,0,0 
ROI_Exists = False    #  Does a region of interest exist due to L mouse up event?  

cv2.namedWindow('Camera')
frame = None

def mouseAction(event,x,y,flags,param):
    global frame, xPos, yPos, valR, valG, valB, rect_corner1, rect_corner2, drawing_rect, ROI_Exists
    if event == cv2.EVENT_LBUTTONDOWN:
        ROI_Exists = False   # DEBUG
        xPos, yPos = x, y
        if frame is not None:
            valB,valG, valR = frame[y,x] 
            red_led.duty_cycle = int(valR/255*MAX_DUTY )
            green_led.duty_cycle = int(valG/255*MAX_DUTY/2)
            blue_led.duty_cycle = int(valB/255*MAX_DUTY/4)
            drawing_rect = True
            rect_corner1 = (x,y)  #save one corner
            rect_corner2 = (x,y)  # so you can always draw rect
    if event == cv2.EVENT_MOUSEMOVE and frame is not None:
        xPos, yPos = x, y      #######DEBUG##########
        valB,valG, valR = frame[y,x]    ##########DEBUG#############
        if drawing_rect:
            rect_corner2 = (x,y)
    if event == cv2.EVENT_LBUTTONUP and frame is not None:
        drawing_rect = False
        rect_corner2 = (x,y)
        ROI_Exists = True
        
    #print(f'{rect_corner1=}, {rect_corner2=}', end = '\r')    ############ DEBUG, ROI coordinates!############
    
cv2.setMouseCallback('Camera',mouseAction)

try:
    while True:
        deltaT = time.time() - tStart
        tStart=time.time()
        fps = fps*.95 + (1/deltaT)*.05
        frame= piCam.capture_array()
        frame=cv2.flip(frame,-1)
        if drawing_rect:
            cv2.rectangle(frame,rect_corner1,rect_corner2,(0,255,0),2)
        myText = f'FPS: {round(fps,1)}'
        text1 = f'Mouse Pos: {(xPos, yPos)}' 
        text2 = f'RGB Pixel Color: {valR, valG, valB}'
        cv2.putText(frame,myText,textLowerLeft,fontFace,fontScale,fontColor,fontThickness)
        cv2.putText(frame,text1,textLowerLeft1,fontFace,fontScale,fontColor,fontThickness)
        cv2.putText(frame,text2,textLowerLeft2,fontFace,fontScale,fontColor,fontThickness)
        cv2.imshow("Camera", frame)
        cv2.moveWindow("Camera",0,TOP_WASTE)
        if ROI_Exists:
            ROI = frame[rect_corner1[1]:rect_corner2[1],rect_corner1[0]:rect_corner2[0]]
            cv2.imshow('ROI',ROI)
            cv2.moveWindow('ROI',W, 0 + TOP_WASTE)
            #print(f'ROI shape: {ROI.shape}', end='\r')    ######DEBUG########
            rows, _, _ = ROI.shape   # columns deep of ROI, needed to stack ROIgray below it
            ROI_Gray = cv2.cvtColor(ROI,cv2.COLOR_BGR2GRAY)
            cv2.imshow('ROIgray',ROI_Gray)
            cv2.moveWindow('ROIgray',W, 0 + TOP_WASTE +rows + WINDOW_WASTE)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
except KeyboardInterrupt:
    cv2.destroyAllWindows()
    piCam.stop()
    red_led.duty_cycle=0
    green_led.duty_cycle=0
    blue_led.duty_cycle = 0
finally:
    print('\nProgram Terminated')
