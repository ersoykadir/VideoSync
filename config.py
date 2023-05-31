import os
import cv2
import socket
import sys

def get_running_mode():
    if len(sys.argv) < 2:
        return 'client'
    return sys.argv[1]
    
class Config:
    WHAT_AM_I = "client"

    CONTROL_PORT = 12345 # for sa and as
    DATA_PORT = 12346 # for video stream

    # VIDEO_RESOLUTION = (854, 480)
    VIDEO_RESOLUTION = (1280, 720)
    # SCREENSHOT_RESOLUTION = (1280, 720)
    SCREENSHOT_RESOLUTION = (1920, 1080)
    VIDEO_FPS = 30
    VIDEO_DURATION = 1 # in seconds

    # Specify video codec
    VIDEO_CODEC = cv2.VideoWriter_fourcc(*"avc1")
    FILE_EXTENSION = ".mp4"
    COMPRESSION_ENABLED = False

    NAME = 'server'

    TEMP_DIR = "temp"
    MY_IP = None


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self) -> None:
        if self.__initialized: return
        self.__initialized = True

        self.WHAT_AM_I = get_running_mode()

        if(not os.path.exists(self.TEMP_DIR)): 
            os.mkdir(self.TEMP_DIR)
        self.MY_IP = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
        if self.MY_IP == '127.0.0.1':
            # Static ip used for virtual machines like wsl, since host ip is not accessible
            print("WSL detected, using static ip!")
            self.MY_IP = '192.168.1.252'
        print("My ip is: ", self.MY_IP)