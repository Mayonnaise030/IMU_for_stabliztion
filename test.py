#!/usr/bin/python3
import time
import serial
import numpy
import sys
import math
import binascii
import struct


startbyte = b'\xfa'
secondbyte = b'\xff'
print("UART Demonstration Program")
print("NVIDIA Jetson Nano Developer Kit")
global recdata
serial_port = serial.Serial(
    # port="/dev/ttyUSB0",
    port="COM13",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
# Wait a second to let the port initialize
time.sleep(1)

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x* 180 / math.pi, pitch_y* 180 / math.pi, yaw_z* 180 / math.pi

class UART:
    def __init__(self):
        self.headingYaw = numpy.zeros(shape=(1,1), dtype='float_')
        self.XsensTime = 0
        self.time_temp = ['' for i in range(1)]
        self.newData = False
        #quat
        self.quat = numpy.zeros(shape=(4), dtype='float_')
        self.quat_temp = ['' for i in range(4)]
        self.quat_temp_bytesToHex = ['' for i in range(4)] 
        self.quat_temp_bytesToASCII = ['' for i in range(4)]

        self.accel = numpy.zeros(shape=(1,4), dtype='float_')
        self.mag = numpy.zeros(shape=(1,4), dtype='float_')
        self.euler = numpy.zeros(shape=(1,3), dtype='float_')
        # #rot
        # self.rot = numpy.zeros(shape=(1,4), dtype='float_')
        # self.rot_temp = ['' for i in range(3)]
        # self.rot_temp_bytesToHex = ['' for i in range(3)] 
        # self.rot_temp_bytesToASCII = ['' for i in range(3)]
        

        self.data_q =  ['' for i in range(16)]
        # self.data_r =  ['' for i in range(9)]
        self.datadt =  ['' for i in range(4)]
        # self.data =  ['' for i in range(12)]
        # self.datadt =  ['' for i in range(4)]
        # self.datanotif = numpy.zeros(shape=(1,4), dtype='uint8')
        # self.datameas = numpy.zeros(shape=(1,256), dtype='uint8')

        self.len = 31
        self.ndx = 0
        self.numbytes = self.len
        self.receivedBytes = ['' for i in range(31)]
        # self.tempBytes = numpy.empty(shape=(1,43), dtype='uint8')
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
                # print(idx," ",int.from_bytes(rc , 'big'), rc ,self.receivedBytes[0])
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

    # def dataswapendian(self, data, length):
    #     cpy =  ['' for i in range(length)]
    #     cpy = data
    #     if length != 4:
    #         temp_len = length//3
    #         for i in range(temp_len):
    #             for j in range(3):
    #                 data[j + i * 3] = cpy[2 - j + i * 3]
    #     else:
    #         temp_len = length//4
    #         for i in range(temp_len):
    #             for j in range(4):
    #                 data[j + i * 4] = cpy[3 - j + i * 4]
            

    def parseData(self):
        # print(self.receivedBytes)
        # SampleTimeFine = 0x1060;
        if self.receivedBytes[4] == b'\x10' and self.receivedBytes[5] == b'\x60' :
            for i in range(4):
                self.datadt[i] = self.receivedBytes[7+i]
            # self.dataswapendian(self.datadt, 4)
            self.time_temp[0] = self.datadt[0] + self.datadt[1] +self.datadt[2] + self.datadt[3]
            self.time_temp[0] = binascii.b2a_hex(self.time_temp[0])
            self.time_temp[0] = self.time_temp[0].decode('ascii')
            self.XsensTime = struct.unpack('!i', bytes.fromhex(self.time_temp[0]))[0]
        
        # QUAT = 0x2010;
        if self.receivedBytes[11] == b'\x20' and self.receivedBytes[12] == b'\x10' :

            for i in range(16):
                self.data_q[i] = self.receivedBytes[14+i] 
            # self.dataswapendian(self.data_q, 12)
            #CONNECT BYTES
            # self.quat_temp[0] = self.data_q[0] + self.data_q[1]   + self.data_q[2] + self.data_q[3]
            # self.quat_temp[1] = self.data_q[4] + self.data_q[5]   + self.data_q[6] + self.data_q[7]
            # self.quat_temp[2] = self.data_q[8] + self.data_q[9]   + self.data_q[10] + self.data_q[11]
            # self.quat_temp[3] = self.data_q[12] + self.data_q[13]  + self.data_q[14] + self.data_q[15]
            self.quat_temp[0] = self.data_q[3] + self.data_q[2]   + self.data_q[1] + self.data_q[0]
            self.quat_temp[1] = self.data_q[7] + self.data_q[6]   + self.data_q[5] + self.data_q[4]
            self.quat_temp[2] = self.data_q[11] + self.data_q[10]   + self.data_q[9] + self.data_q[8]
            self.quat_temp[3] = self.data_q[15] + self.data_q[14]  + self.data_q[13] + self.data_q[12]
            # print('haha',self.quat_temp)
            
            # self.quat_temp[0] = binascii.b2a_hex(self.data_q[3]) + binascii.b2a_hex(self.data_q[2])   + binascii.b2a_hex(self.data_q[1]) + binascii.b2a_hex(self.data_q[0])
            # self.quat_temp[1] = binascii.b2a_hex(self.data_q[7]) + binascii.b2a_hex(self.data_q[6])   + binascii.b2a_hex(self.data_q[5]) + binascii.b2a_hex(self.data_q[4])
            # self.quat_temp[2] = binascii.b2a_hex(self.data_q[11]) + binascii.b2a_hex(self.data_q[10])   + binascii.b2a_hex(self.data_q[9]) + binascii.b2a_hex(self.data_q[8])
            # self.quat_temp[3] = binascii.b2a_hex(self.data_q[15]) + binascii.b2a_hex(self.data_q[14])   + binascii.b2a_hex(self.data_q[13]) + binascii.b2a_hex(self.data_q[12])

            # self.quat_temp[0] = binascii.b2a_hex(self.data_q[0]) + binascii.b2a_hex(self.data_q[1])   + binascii.b2a_hex(self.data_q[2]) + binascii.b2a_hex(self.data_q[3])
            # self.quat_temp[1] = binascii.b2a_hex(self.data_q[4]) + binascii.b2a_hex(self.data_q[5])   + binascii.b2a_hex(self.data_q[6]) + binascii.b2a_hex(self.data_q[7])
            # self.quat_temp[2] = binascii.b2a_hex(self.data_q[8]) + binascii.b2a_hex(self.data_q[9])   + binascii.b2a_hex(self.data_q[10]) + binascii.b2a_hex(self.data_q[11])
            # self.quat_temp[3] = binascii.b2a_hex(self.data_q[12]) + binascii.b2a_hex(self.data_q[13])   + binascii.b2a_hex(self.data_q[14]) + binascii.b2a_hex(self.data_q[15])
            #HEX
            self.quat_temp_bytesToHex[0] = binascii.b2a_hex(self.quat_temp[0])
            self.quat_temp_bytesToHex[1] = binascii.b2a_hex(self.quat_temp[1])
            self.quat_temp_bytesToHex[2] = binascii.b2a_hex(self.quat_temp[2])
            self.quat_temp_bytesToHex[3] = binascii.b2a_hex(self.quat_temp[3])
            # print('hahaha',self.quat_temp_bytesToHex)
            #ascii decode
            self.quat_temp_bytesToASCII[0] = self.quat_temp_bytesToHex[0].decode('ascii')
            self.quat_temp_bytesToASCII[1] = self.quat_temp_bytesToHex[1].decode('ascii')
            self.quat_temp_bytesToASCII[2] = self.quat_temp_bytesToHex[2].decode('ascii')
            self.quat_temp_bytesToASCII[3] = self.quat_temp_bytesToHex[3].decode('ascii')
            # self.quat_temp_bytesToASCII[0] = self.quat_temp[0].decode('ascii')
            # self.quat_temp_bytesToASCII[1] = self.quat_temp[1].decode('ascii')
            # self.quat_temp_bytesToASCII[2] = self.quat_temp[2].decode('ascii')
            # self.quat_temp_bytesToASCII[3] = self.quat_temp[3].decode('ascii')
            # print('hahaha',self.quat_temp_bytesToASCII)
            #to float
            self.quat[0] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[0]))[0]
            self.quat[1] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[1]))[0]
            self.quat[2] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[2]))[0]
            self.quat[3] = struct.unpack('<f', bytes.fromhex(self.quat_temp_bytesToASCII[3]))[0]
            # print(self.quat)

        # Rot = 0x8020;
        # if self.receivedBytes[30] == b'\x80' and self.receivedBytes[31] == b'\x20' :
        #     for i in range(9):
        #         self.data_r[i] = self.receivedBytes[33+i] 
        #     # self.dataswapendian(self.data_r, 9)
        #     #CONNECT BYTES
        #     self.rot_temp[0] = self.data_r[0] + self.data_r[1]  + self.data_r[2] + self.data_r[3]
        #     self.rot_temp[1] = self.data_r[4] + self.data_r[5]  + self.data_r[6] + self.data_r[3]
        #     self.rot_temp[2] = self.data_r[6] + self.data_r[7]  + self.data_r[8] + self.data_r[3]
        #     #reverse
        #     self.rot_temp[0] = self.rot_temp[0][::-1]
        #     self.rot_temp[1] = self.rot_temp[1][::-1]
        #     self.rot_temp[2] = self.rot_temp[2][::-1]
        #     print('haha',self.rot_temp)
        #     #HEX
        #     self.rot_temp_bytesToHex[0] = binascii.b2a_hex(self.rot_temp[0])
        #     self.rot_temp_bytesToHex[1] = binascii.b2a_hex(self.rot_temp[1])
        #     self.rot_temp_bytesToHex[2] = binascii.b2a_hex(self.rot_temp[2])
        #     print('hahaha',self.rot_temp_bytesToHex)
        #     #ascii decode
        #     self.rot_temp_bytesToASCII[0] = self.rot_temp_bytesToHex[0].decode('ascii')
        #     self.rot_temp_bytesToASCII[1] = self.rot_temp_bytesToHex[1].decode('ascii')
        #     self.rot_temp_bytesToASCII[2] = self.rot_temp_bytesToHex[2].decode('ascii')
        #     print('hahaha',self.rot_temp_bytesToASCII)
        #     #to float
        #     self.rot[0,0] = struct.unpack('!f', bytes.fromhex(self.rot_temp_bytesToASCII[0]))[0]
        #     self.rot[0,1] = struct.unpack('!f', bytes.fromhex(self.rot_temp_bytesToASCII[1]))[0]
        #     self.rot[0,2] = struct.unpack('!f', bytes.fromhex(self.rot_temp_bytesToASCII[2]))[0]
        #     print(self.rot)

    def QuatToEuler (self):
        self.parseData()
        w = self.quat[0]
        x = self.quat[1]
        y = self.quat[2]
        z = self.quat[3]
        
        # print(w,x,y,z)
        # roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        self.euler[0,0] = math.atan2(sinr_cosp, cosr_cosp)
        # pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            self.euler[0,1] = math.copysign(math.pi / 2, sinp); # use 90 degrees if out of range
        else:
            self.euler[0,1] = math.asin(sinp)
        #yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        self.euler[0,2] = math.atan2(siny_cosp, cosy_cosp)

if __name__ == "__main__":
    xsens = UART()
    while 1:
        xsens.getmeasure()
        time.sleep(0.01)
        if xsens.newData == True:
            xsens.newData = False
            xsens.QuatToEuler ()
            # print(xsens.XsensTime*1e-4)
            print("ROLL[0]:",(xsens.euler[0,0] * 180 / math.pi)," PITCH[1]:",(xsens.euler[0,1] * 180 / math.pi)," YAW[2]:",(xsens.euler[0,2] * 180 / math.pi))
            # print("rot[0]:",xsens.rot[0,0] * 180 / math.pi," rot[1]:",xsens.rot[0,1] * 180 / math.pi,"rot[2]:",xsens.rot[0,2] * 180 / math.pi)
    