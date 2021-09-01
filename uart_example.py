#!/usr/bin/python3
import time
import serial
startbyte = b'\xfa'
secondbyte = b'\xff'
len = 43
print("UART Demonstration Program")
print("NVIDIA Jetson Nano Developer Kit")
global recdata
serial_port = serial.Serial(
    port="/dev/ttyUSB0",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
# Wait a second to let the port initialize
time.sleep(1)

def getmeasure():
    global recdata
    recvINprogress = False 
    recvINprogress2 = False
    data = None
    data = serial_port.read()
    ndx = 0
    newData = False
    recdata = []
    while data != None and newData == False:
        data = serial_port.read()
        if data == startbyte:
            recvINprogress = True
            recdata.append(b'\xfa') 

        if data == secondbyte and recvINprogress == True:
            recvINprogress2 == True

        if recvINprogress == True and recvINprogress2 == True:
            if(ndx < len):
                recdata.append(data)
                ndx += 1
            else: 
                recvINprogress = False 
                recvINprogress2 = False
                ndx = 1
                newData = True
try:
    # Send a simple header
    serial_port.write("UART Demonstration Program\r\n".encode())
    serial_port.write("NVIDIA Jetson Nano Developer Kit\r\n".encode())
    while True:
        if serial_port.inWaiting() > 0:
            data = serial_port.read()
            data2 = int.from_bytes(data , 'big')
            print(data2)
            serial_port.write(data)
            # if we get a carriage return, add a line feed too
            # \r is a carriage return; \n is a line feed
            # This is to help the tty program on the other end 
            # Windows is \r\n for carriage return, line feed
            # Macintosh and Linux use \n
            if data == "\r".encode():
                # For Windows boxen on the other end
                serial_port.write("\n".encode())


except KeyboardInterrupt:
    print("Exiting Program")

except Exception as exception_error:
    print("Error occurred. Exiting Program")
    print("Error: " + str(exception_error))

finally:
    serial_port.close()
    pass
