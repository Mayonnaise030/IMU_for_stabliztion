import sys
import math
import binascii
import struct
import numpy

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


quat = numpy.zeros(shape=(4), dtype='float_')
quat_temp = [b'\xa7j\x7f?', b'\xdc\x8a@\xbc', b'.\x10\x88=', b'lJI\xba']
quat_temp_bytesToHex = ['' for i in range(4)] 
quat_temp_bytesToASCII = ['' for i in range(4)]
euler = numpy.zeros(shape=(3), dtype='float_')
a = [b'?',b't',b'\x84',b'\xfb']
b = [b'\xbe',b'/',b'p',b'\xf4']
c = [b'\xbe',b'Y',b'\r',b'\x88']
d = [b'\xbd', b'\xed',b'\r',b'\r']

# quat_temp[0] =  b'7\xc8~?'
# quat_temp[1] =  b'\xb8K\xe9\xbb'
# quat_temp[2] =  b'\xa0$\xc6='
# quat_temp[3] =  b'\xdc*\x84\xbb'

quat_temp[0] = quat_temp[0][::-1]
quat_temp[1] = quat_temp[1][::-1]
quat_temp[2] = quat_temp[2][::-1]
quat_temp[3] = quat_temp[3][::-1]


quat_temp_bytesToHex[0] = binascii.b2a_hex(quat_temp[0])
quat_temp_bytesToHex[1] = binascii.b2a_hex(quat_temp[1])
quat_temp_bytesToHex[2] = binascii.b2a_hex(quat_temp[2])
quat_temp_bytesToHex[3] = binascii.b2a_hex(quat_temp[3])

quat_temp_bytesToASCII[0] = quat_temp_bytesToHex[0].decode('ascii')
quat_temp_bytesToASCII[1] = quat_temp_bytesToHex[1].decode('ascii')
quat_temp_bytesToASCII[2] = quat_temp_bytesToHex[2].decode('ascii')
quat_temp_bytesToASCII[3] = quat_temp_bytesToHex[3].decode('ascii')

quat[0] = struct.unpack('!f', bytes.fromhex(quat_temp_bytesToASCII[0]))[0]
quat[1] = struct.unpack('!f', bytes.fromhex(quat_temp_bytesToASCII[1]))[0]
quat[2] = struct.unpack('!f', bytes.fromhex(quat_temp_bytesToASCII[2]))[0]
quat[3] = struct.unpack('!f', bytes.fromhex(quat_temp_bytesToASCII[3]))[0]
print('ha',quat)


w = quat[0]
x = quat[1]
y = quat[2]
z = quat[3]
print(w,x,y,z)
# # roll (x-axis rotation)
# sinr_cosp = 2 * (w * x + y * z)
# cosr_cosp = 1 - 2 * (x * x + y * y)
# euler[0] = math.atan2(sinr_cosp, cosr_cosp)
# # pitch (y-axis rotation)
# sinp = 2 * (w * y - z * x)
# if abs(sinp) >= 1:
#     euler[1] = math.copysign(math.pi / 2, sinp); # use 90 degrees if out of range
# else:
#     euler[1] = math.asin(sinp)
# #yaw (z-axis rotation)
# siny_cosp = 2 * (w * z + x * y)
# cosy_cosp = 1 - 2 * (y * y + z * z)
# euler[2] = math.atan2(siny_cosp, cosy_cosp)
euler[0],euler[1],euler[2] =  euler_from_quaternion(x,y,z,w)

print ("this is roll: %f this is pitch: %f this is yaw:",euler[0],euler[1],euler[2] )