#!/usr/bin/python3
import cv2
import os
import time
import sys
import struct
import RPi.GPIO as GPIO
import time
import threading
from imu import *

path = 'mission_number/num_of_mission.txt'                           #to get the nums of round(frame)).start()

#  設定 I/O腳位
# Pin Definitons:
but_pin = 7  # BOARD pin 7
led_1_code_run = 12     # BOARD pin 12
led_2_but_trigger = 18  # BOARD pin 18
def GPIO_main():
    GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
    GPIO.setup(but_pin, GPIO.IN)  # Button pin set as input
    GPIO.setup(led_1_code_run, GPIO.OUT)  # LED pin set as output
    GPIO.setup(led_2_but_trigger, GPIO.OUT)  # LED Button trigger set as output
    # Initial state for LEDs:
    GPIO.output(led_1_code_run, GPIO.LOW)
    GPIO.output(led_2_but_trigger, GPIO.LOW)

mutex = threading.Lock()

class Webcam:
    def __init__(self,cam_num=0) :
        self.cap =   cv2.VideoCapture(cam_num)
        self.fourcc =cv2.VideoWriter_fourcc('P','I','M','1')  # 使用 PIM1 編碼
        # self.cap.set(cv2.CAP_PROP_FOURCC, self.fourcc) # 設定擷取影像的尺寸大小
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 設定擷取影像的尺寸大小
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 

    def run(self,filename):
        while(1):
            ret, frame =self.cap.read()
            if ret  == True:
                    self.write(frame)
                    ret = False
                    mutex.acquire()
                    filename.write("!\n")   #store imu_data
                    mutex.release()

    def run2(self):
        while(1):
            ret, frame =self.cap.read()
            if ret  == True:
                    self.write(frame)
                    ret = False

    def write_set(self,video_num,Dir):
        self.out = cv2.VideoWriter( Dir + str(video_num) + '.avi' ,  self.fourcc, 30.0, (640, 480))  # FPS 值為 30.0，解析度為 640x480

    def write(self,frame):
        self.out.write(frame) # 寫入影像

    def stop(self):
        self.cap.release()
        self.out.release()


if __name__ == "__main__":
    xsens = UART()     # initial the imu class
    # Pin Setup:
    GPIO_main()          # set GPIO:
    try:
        while(True):
            xsens.getmeasure()
            xsens.QuatToEuler ()
            but_value = GPIO.input(but_pin)    # 讀取按鈕狀態
            GPIO.output(led_1_code_run,GPIO.HIGH)
            
            if but_value ==  1 :
                GPIO.output(led_2_but_trigger,GPIO.HIGH)
                #get how many times we collect data
                f_imu = open(path, 'r')
                text = []
                for line in f_imu:
                    text.append(line)
                num_of_mission = int(text[0])
                num_of_mission = num_of_mission + 1  #set nums of mission
                f_imu.close()
                #record nums of mission
                f_imu = open(path, 'w')
                f_imu.write(str(num_of_mission))
                f_imu.close()

                #record imu from this mission
                imu_data = open('./imu_data/imu_data_'+str(num_of_mission)+'.txt','w')

                print("action! round " , num_of_mission)
                camera = Webcam(0)
                time.sleep(0.1)
                camera2 = Webcam(3)
                print( 'video_num:' ,num_of_mission)
                camera.write_set(num_of_mission,'./stable/')    # 輸入影像編號
                camera2.write_set(num_of_mission,'./unstable/')    # 輸入影像編號
                
                threading.Thread(target= camera.run,args=(imu_data,)).start()
                threading.Thread(target= camera2.run2).start()
                while(True):
                    xsens.getmeasure()
                    if xsens.newData == True:
                        xsens.newData = False
                        xsens.QuatToEuler ()
                        # print(xsens.XsensTime*1e-4)
                        s = ""
                        s += str(time.time()) + " |Roll: %.2f" % (xsens.euler[0,0] * 180 / math.pi) + ", Pitch: %.2f" % (xsens.euler[0,1] * 180 / math.pi) + ", Yaw: %.2f " % (xsens.euler[0,2] * 180 / math.pi )
                        mutex.acquire()
                        imu_data.write("%s\n" % s)   #store imu_data
                        mutex.release()
                    but_value = GPIO.input(but_pin)
                    if  but_value ==  0 :
                        print("Cut!")
                        break
                camera.stop()
                camera2.stop()
            else: 
                GPIO.output(led_1_code_run,GPIO.LOW)
                GPIO.output(led_2_but_trigger, GPIO.LOW)
    finally:
        GPIO.cleanup()  # cleanup all GPIO