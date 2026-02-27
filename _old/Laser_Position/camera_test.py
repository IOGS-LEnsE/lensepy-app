# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 14:05:45 2023

@author: julien.villemejane
"""
import cv2
# pip install windows-capture-device-list
# https://pypi.org/project/windows-capture-device-list/
import device

'''
apiPreference    preferred Capture API backends to use. 
Can be used to enforce a specific reader implementation 
if multiple are available: 
e.g. cv2.CAP_MSMF or cv2.CAP_DSHOW.
'''
# open video0
cap = cv2.VideoCapture(1, cv2.CAP_MSMF)
# set width and height
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# set fps
# cap.set(cv2.CAP_PROP_FPS, 30)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
