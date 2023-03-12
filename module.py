import cv2
import mediapipe as mp
import math
import numpy

# import for pycaw from github: https://github.com/AndreMiras/pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# print(volume.GetMute())
# print(volume.GetMasterVolumeLevel())
# print(volume.GetVolumeRange())
# volume.SetMasterVolumeLevel(-65.25, None)

cap =cv2.VideoCapture(0)

mpDraw = mp.solutions.drawing_utils
mpHands = mp.solutions.hands
hands = mpHands.Hands()

while True:
    success,img = cap.read()
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    #detected palm
    results = hands.process(imgRGB)
    #if palm is detected
    if results.multi_hand_landmarks:
        #loop through all the hands
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h,w,c = img.shape
                cx,cy = int(lm.x*w) , int(lm.y*h)
                lmList.append([id,cx,cy])

                # print(id, lm)
                # mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            if lmList:
                #co-ordinates of thumb
                x1,y1 = lmList[4][1], lmList[4][2] 
                #co-ordinates of fore-finger
                x2,y2 = lmList[8][1], lmList[8][2]
                #circle around thumb tip
                cv2.circle(img,(x1,y1),15,(1,23,123),cv2.FILLED)
                #circle around fore-finger tip
                cv2.circle(img,(x2,y2),15,(1,23,123),cv2.FILLED)
                #line b/w two tips
                cv2.line(img,(x1,y1),(x2,y2),(1,23,123),4)
                z1,z2 = (x1+x2)//2, (y1+y2)//2
                length = math.hypot(x2-x1, y2-y1)
                # print(length)
            
            # length ranges from 50-300,, 50 signifies 0 or min and 300 signifies 100 or max volume
            # when length is 50---> lib(pycaw) is -65.25 ---> system volume is 0
            # when length is 300---> lib(pycaw) is 0.0 ---> system volume is 100
            volRange = volume.GetVolumeRange()
            minVol = volRange[0]
            maxVol = volRange[1]
            vol = numpy.interp(length, [50,100], [minVol, maxVol])
            volPer = numpy.interp(length, [50,100], [0,100])
            volBar = numpy.interp(length, [50,300], [400,150])

            volume.SetMasterVolumeLevel(vol, None)
            cv2.putText(img, str(int(volPer)), (40,450), cv2.FONT_HERSHEY_COMPLEX, 2, (1,3,5), 3)
            cv2.rectangle(img, (50,150), (85,400) ,(123,213,122), 3)
            cv2.rectangle(img, (50, int(volBar)), (85,400) ,(0,231,23), cv2.FILLED)
                

    cv2.imshow("Gesture sound control", img)
    cv2.waitKey(1)