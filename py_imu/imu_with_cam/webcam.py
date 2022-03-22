#set webcam class
import cv2
class Webcam:
    def __init__(self,cam_num=0) :
        self.cap =   cv2.VideoCapture(cam_num)
        self.fourcc =cv2.VideoWriter_fourcc('P','I','M','1')  # 使用 PIM1 編碼
        # self.cap.set(cv2.CAP_PROP_FOURCC, self.fourcc) # 設定擷取影像的尺寸大小
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 設定擷取影像的尺寸大小
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 

    def write_set(self,video_num,Dir):
        self.out = cv2.VideoWriter( Dir + str(video_num) + '.avi' ,  self.fourcc, 30.0, (640, 480))  # FPS 值為 30.0，解析度為 640x480

    def write(self,frame):
        self.out.write(frame) # 寫入影像

    # def write(self,filename):
    #     ret, frame = self.cap.read()
    #     if ret == True:
    #         self.out.write(frame) # 寫入影像
    #         filename.write("%s\n" % "camera 1 data input")

    # def available(self):
    #     ret, frame = self.cap.read()
        # return True if ret  else False
    
    def stop(self):
        self.cap.release()
        self.out.release()