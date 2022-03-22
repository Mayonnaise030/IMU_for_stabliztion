#!/usr/bin/python3
import cv2
import os
import time
import sys
import struct
import time
import threading
from imu import *


mutex = threading.Lock()


if __name__ == "__main__":
    xsens = UART()     # initial the imu class
    while(True):
        xsens.getmeasure()
        xsens.QuatToEuler ()
        time.sleep(1/1000000)
        while(True):
            xsens.getmeasure()
            time.sleep(1/100000)
            if xsens.newData == True:
                xsens.newData = False
                xsens.QuatToEuler ()
                # print(xsens.XsensTime*1e-4)
                s = ""
                s += str(time.time()) + " |Roll: %.2f" % (xsens.euler[0,0] * 180 / math.pi) + ", Pitch: %.2f" % (xsens.euler[0,1] * 180 / math.pi) + ", Yaw: %.2f " % (xsens.euler[0,2] * 180 / math.pi )
                print(s)
                