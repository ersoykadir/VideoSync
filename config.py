import os
import cv2
import socket

class Config:
    WHAT_AM_I = "server"

    CONTROL_PORT = 12345 # for sa and as
    DATA_PORT = 12346 # for video stream

    VIDEO_RESOLUTION = (1000, 1000)
    VIDEO_FPS = 30
    VIDEO_DURATION = 1 # in seconds

    # Specify video codec
    VIDEO_CODEC = cv2.VideoWriter_fourcc(*"avc1")
    FILE_EXTENSION = ".mp4"
    COMPRESSION_ENABLED = False

    NAME = 'kadir'

    TEMP_DIR = "temp"
    MY_IP = None


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            print('init init')
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self) -> None:
        if self.__initialized: return
        self.__initialized = True


        if(not os.path.exists(self.TEMP_DIR)): 
            os.mkdir(self.TEMP_DIR)
        self.MY_IP = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
        if self.MY_IP == '127.0.0.1':
            # Static ip used for virtual machines like wsl, since host ip is not accessible
            print("WSL detected, using static ip!")
            self.MY_IP = '192.168.1.59'
        print("My ip is: ", self.MY_IP)
    
Config()