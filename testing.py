#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:00:01 2023

@author: hemant.jaiman
"""

import numpy as np
import HandTracking as htm
import time
import autopy
import cv2
import pyautogui
import math
import cvzone

X = [300,245,200,170,145,130,112,103,93,87,80,75,70,67,62,59,57]
Y = [20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

coff= np.polyfit(X,Y,2) ## Ax2+bX+C
A,B,C = coff
##########################
wCam, hCam = 640, 480
frameR = 100 # Frame Reduction
smoothening = 7
#########################
 
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
 
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)
timer = 0
## for thumbup back button stime=0 
stime = 0
while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        timer = 0
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        #detecting thumb
        x4, y4 = lmList[4][1:]

        # print(x1, y1, x2, y2)
        #print(x4,y4)
        
        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        print(fingers)

        _,point5x,point5y = lmList[5]
        _,point17x,point17y = lmList[17]

        dist = int(math.sqrt((point17y-point5y)**2 + (point17x-point5x)**2)) 
        distance = detector.Hand_Distance(dist,A,B,C)
        print("Distance is:",distance)
        cvzone.putTextRect(img,f"{int(distance)}cm",(bbox[0]+10,bbox[1]-20))

        if int(distance) < 90:
            # print(fingers)
            #cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),(255, 0, 255), 2)
            # 4. Only Index Finger : Moving Mode
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                # 5. Convert Coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                # 6. Smoothen Values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
            
                # 7. Move Mouse
                autopy.mouse.move(wScr - clocX, clocY)
                #cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY
            
            # 8. when all fingers are closed : Clicking Mode
            if  fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3]== 0:
                
                autopy.mouse.click()
                time.sleep(1)
            
            if fingers[0] == 1 and fingers[1] == 1:
                length, img, lineInfo = detector.findDistance(8, 4, img)

                # 5. Convert Coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                # 6. Smoothen Values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                if length < 20:
                    autopy.mouse.toggle(down=True)
                    autopy.mouse.move(wScr - clocX, clocY)
                else:
                    autopy.mouse.toggle(down=False)
            
            ### giving direction with point 0 and point 8
            if fingers[1] == 1 and fingers[0] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0 and detector.get_left_dir(0,8,img):
                pyautogui.hscroll(10)
                time.sleep(0.5)
            if fingers[1] == 1 and fingers[0] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0 and detector.get_right_dir(0,8,img):
                pyautogui.hscroll(-10)
                time.sleep(0.5)
            
            ### going back with thumb
            if fingers[0] == 1 and detector.get_thumbsup(1,17,img):
                pyautogui.hotkey('command', 'left')
                    


    if len(lmList) == 0:
        timer = timer + 1
        if timer > 200:
            pyautogui.hotkey('command', 'left')
            timer = 0

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 0), 3)
    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)