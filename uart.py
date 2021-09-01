#!/usr/bin/python3
import time
import serial
import numpy
import sys
import math
import struct

startbyte = b'\xfa'
secondbyte = b'\xff'
len = 43
print("UART Demonstration Program")
print("NVIDIA Jetson Nano Developer Kit")
global recdata
serial_port = serial.Serial(
    # port="/dev/ttyUSB0",
    port="COM5",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
# Wait a second to let the port initialize
time.sleep(1)

class UART:
    def __init__(self):
        self.headingYaw = numpy.empty(shape=(1,1), dtype='float_')
        self.XsensTime = numpy.empty(shape=(1,1), dtype='float_')
        self.newData = False

        self.quat = numpy.empty(shape=(1,4), dtype='float_')
        self.accel = numpy.empty(shape=(1,4), dtype='float_')
        self.mag = numpy.empty(shape=(1,4), dtype='float_')
        self.rot = numpy.empty(shape=(1,4), dtype='float_')
        self.euler = numpy.empty(shape=(1,4), dtype='float_')

        self.data = numpy.empty(shape=(1,4), dtype='uint8')
        self.datadt = numpy.empty(shape=(1,4), dtype='uint8')
        self.datanotif = numpy.empty(shape=(1,4), dtype='uint8')
        self.datameas = numpy.empty(shape=(1,256), dtype='uint8')

        self.len = 43
        self.ndx = 0
        self.numbytes = self.len
        self.receivedBytes = numpy.chararray((1, 43))
        self.tempBytes = numpy.empty(shape=(1,43), dtype='uint8')
        pass

    def getmeasure(self):
        recvINprogress = False 
        recvINprogress2 = False
        rc = serial_port.read()
        self.ndx = 0
        while rc != None and self.newData == False:
            rc = serial_port.read()
            
            if rc == startbyte:
                recvINprogress = True
                self.receivedBytes[0,0] = startbyte

            if rc == secondbyte and recvINprogress == True:
                recvINprogress2 = True
            if recvINprogress == True and recvINprogress2 == True:
                if self.ndx < self.len:
                    self.receivedBytes[0,self.ndx] = rc 
                    
                    self.ndx = self.ndx+1
                else: 
                    recvINprogress = False 
                    recvINprogress2 = False
                    self.ndx = 1
                    self.newData = True

    def dataswapendian(self, data, length):
        cpy = numpy.empty(shape=(1,length), dtype='uint8')
        cpy[:length] = struct.pack('!h', data)
        for i in range(length):
            for j in range(4):
                data[j + i * 4] = cpy[3 - j + i * 4]
            

    def parseData(self):

        # SampleTimeFine = 0x1060;
        if self.receivedBytes[0,4] == b'\x10' and self.receivedBytes[0,5] == b'\x60' :
            for i in range(4):
                self.datadt[i] = int.from_bytes(self.receivedBytes[7+i] , 'big')
        self.dataswapendian(self.datadt, int(sys.getsizeof( float())))
        self.XsensTime = int.from_bytes(self.datadt , 'big')

        # QUAT = 0x2010;
        if self.receivedBytes[0,11] == b'\x20' and self.receivedBytes[0,12] == b'\x10' :
            for i in range(16):
                self.datadt[i] = int.from_bytes(self.receivedBytes[0,14+i] , 'big')
        self.dataswapendian(self.data, int(sys.getsizeof( float()))*4)
        self.quat[:int(sys.getsizeof( float()))*4] = self.data

        # QUAT = 0x8020;
        if self.receivedBytes[0,11] == b'\x80' and self.receivedBytes[0,12] == b'\x20' :
            for i in range(12):
                self.data[i] = int.from_bytes(self.receivedBytes[0,33+i] , 'big')
        self.dataswapendian(self.data, int(sys.getsizeof( float()))*3)
        self.rot[:int(sys.getsizeof( float()))*3] = self.data

    def QuatToEuler (self):
        self.parseData()
        w = self.quat[0]
        x = self.quat[1]
        y = self.quat[2]
        z = self.quat[3]

        # roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        self.euler[0] = math.atan2(sinr_cosp, cosr_cosp)
        # pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            self.euler[1] = math.copysign(math.pi / 2, sinp); # use 90 degrees if out of range
        else:
            self.euler[1] = math.asin(sinp)
        #yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        self.euler[2] = math.atan2(siny_cosp, cosy_cosp)

if __name__ == "__main__":
    xsens = UART()
    while 1:
        xsens.getmeasure()
        if xsens.newData == True:
            xsens.newData = False
            xsens.QuatToEuler ()
            print(xsens.XsensTime[0]*1e-4); print(" , ")
            print(xsens.euler[0] * 180 / math.pi); print(" , ")
            print(xsens.euler[1] * 180 / math.pi); print(" , ")
            print(xsens.euler[2] * 180 / math.pi); print(" , ")
            print(xsens.rot[0] * 180 / math.pi); print(" , ")
            print(xsens.rot[1] * 180 / math.pi); print(" , ")
            print(xsens.rot[2] * 180 / math.pi); print(" , ")
            print("\n")
        time.sleep(10);
    