import time
import serial
import numpy
import sys
import math
import binascii
import struct
import RPi.GPIO as GPIO

path = 'mission_number/num_of_mission.txt'                          # to get the nums of round

# Pin Definitons:
but_pin = 7  # BOARD pin 7
led_1_code_run = 12     # BOARD pin 12
led_2_but_trigger = 18  # BOARD pin 18

#set the detail of serial
serial_port = serial.Serial(
    port="/dev/ttyUSB1",                    #set the port
    baudrate=115200,                           #set the baudrate
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)

# Wait a second to let the port initialize
time.sleep(0.1)

startbyte = b'\xfa'                               #set the first check point
secondbyte = b'\xff'                          #set the second check point

#set uart class
class UART:
    def __init__(self):
        self.newData = False   #確認是否有獲取資料
        
        # -------四方位角得紀錄及換算變數-------
        self.quat = numpy.zeros(shape=(4), dtype='float_')
        self.quat_temp = ['' for i in range(4)]
        self.quat_temp_bytesToHex = ['' for i in range(4)] 
        self.quat_temp_bytesToASCII = ['' for i in range(4)]

        self.data_q =  ['' for i in range(16)]
        self.datadt =  ['' for i in range(4)]

        self.euler = numpy.zeros(shape=(1,3), dtype='float_')

        self.len = 31    #確認資料長度
        self.ndx = 0
        self.receivedBytes = ['' for i in range(31)]
        pass

    def getmeasure(self):
        recvINprogress = False 
        recvINprogress2 = False
        idx = 0
        while serial_port.in_waiting > 0 and self.newData == False:
            rc = serial_port.read()
            if rc == startbyte:
                recvINprogress = True
                self.receivedBytes[0] = startbyte
            if recvINprogress == True and rc == secondbyte:
                recvINprogress2 = True

            if recvINprogress == True and recvINprogress2 == True:
                if self.ndx < self.len:
                    self.receivedBytes[self.ndx] = rc 
                    #print(rc)
                    idx += 1
                    # print(idx," ",int.from_bytes(rc , 'big'), rc.hex() ,self.receivedBytes[self.ndx])
                    self.ndx = self.ndx+1
                else: 
                    recvINprogress = False 
                    recvINprogress2 = False
                    self.ndx = 1
                    idx = 0
                    self.newData = True

    def parseData(self):
       
        # -----QUAT = 0x2010-----
        if self.receivedBytes[11] == b'\x20' and self.receivedBytes[12] == b'\x10' :

            for i in range(16):
                self.data_q[i] = self.receivedBytes[14+i]      #進行資料的讀取

            #-----LINK BYTES-----
            self.quat_temp[0] = self.data_q[3] + self.data_q[2]   + self.data_q[1] + self.data_q[0]
            self.quat_temp[1] = self.data_q[7] + self.data_q[6]   + self.data_q[5] + self.data_q[4]
            self.quat_temp[2] = self.data_q[11] + self.data_q[10]   + self.data_q[9] + self.data_q[8]
            self.quat_temp[3] = self.data_q[15] + self.data_q[14]  + self.data_q[13] + self.data_q[12]
            
            #-----Transfer to HEX -----
            self.quat_temp_bytesToHex[0] = binascii.b2a_hex(self.quat_temp[0])
            self.quat_temp_bytesToHex[1] = binascii.b2a_hex(self.quat_temp[1])
            self.quat_temp_bytesToHex[2] = binascii.b2a_hex(self.quat_temp[2])
            self.quat_temp_bytesToHex[3] = binascii.b2a_hex(self.quat_temp[3])
            # print('hahaha',self.quat_temp_bytesToHex)

            #-----use ascii decode-----
            self.quat_temp_bytesToASCII[0] = self.quat_temp_bytesToHex[0].decode('ascii')
            self.quat_temp_bytesToASCII[1] = self.quat_temp_bytesToHex[1].decode('ascii')
            self.quat_temp_bytesToASCII[2] = self.quat_temp_bytesToHex[2].decode('ascii')
            self.quat_temp_bytesToASCII[3] = self.quat_temp_bytesToHex[3].decode('ascii')
            # print('hahaha',self.quat_temp_bytesToASCII)

            #-----unpack data to float-----
            self.quat[0] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[0]))[0]
            self.quat[1] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[1]))[0]
            self.quat[2] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[2]))[0]
            self.quat[3] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[3]))[0]
            # print(self.quat)

#Let Quat to euler angle
    def QuatToEuler (self):  
        self.parseData()
        w = self.quat[0]
        x = self.quat[1]
        y = self.quat[2]
        z = self.quat[3]
        
        # -----進行四方位角到euler 角的運算------
        # roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        self.euler[0,0] = math.atan2(sinr_cosp, cosr_cosp)
        # pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            self.euler[0,1] = math.copysign(math.pi / 2, sinp);  # use 90 degrees if out of range
        else:
            self.euler[0,1] = math.asin(sinp)
        #yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        self.euler[0,2] = math.atan2(siny_cosp, cosy_cosp)

    # 讀取目前任務編碼並回傳
    def read_mission_times(self):
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
        return  num_of_mission

    # 設定gpio pin mode
    def Gpio_setup(self):
        GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
        GPIO.setup(but_pin, GPIO.IN)  # Button pin set as input
        GPIO.setup(led_1_code_run, GPIO.OUT)  # LED pin set as output
        GPIO.setup(led_2_but_trigger, GPIO.OUT)  # LED Button trigger set as output
        # Initial state for LEDs:
        GPIO.output(led_1_code_run, GPIO.LOW)
        GPIO.output(led_2_but_trigger, GPIO.LOW)