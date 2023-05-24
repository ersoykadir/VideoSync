from __future__ import annotations

import time
from threading import Thread

from utils.send_packet import send_packet

from config import Config
from utils import video_recorder,perfect_sleep
from connection import Connection

class Server:
    last = time.perf_counter()
    currently_recording = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self):
        if self.__initialized: return
        self.__initialized = True

        Thread(target=self.start_recording).start()

    def start_video(self):
        self.currently_recording = True

    def start_recording(self):
        if Server().currently_recording:
            print("Server:","\tAlready recording!")
            return

        Server().currently_recording = True
        print("Server:","\tStarting recording!")

        while True:
            if Server().currently_recording == False:
                print("Server:","\tStopping recording!")
                break

            if len(Connection().connected_ips) == 0:
                print("Server:","\tNo connected clients, waiting!")
                time.sleep(1) # wait for 1 second and check again
                continue

            recorded_file = video_recorder.record()
            Thread(target=Server().send_video_to_users, args=(recorded_file,)).start()
            
            
    def send_video_to_users(self, recorded_file):
        # perfect_sleep.perfect_sleep(2) # wait for 1 second and check again
        s = time.perf_counter()
        time.sleep(2)
        print(time.perf_counter()-s)
        print(time.perf_counter()-Server().last)
        Server().last = time.perf_counter()

        f = open(recorded_file, 'rb')
        file_bytes = f.read()
        f.close()

        for ip in Connection().connected_ips.keys():
            send_packet(ip, Config().DATA_PORT, file_bytes)

    def stop_recording(self):
        self.currently_recording = False
