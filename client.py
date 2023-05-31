import socket
from threading import Thread
import time
import vlc
from config import Config

class Client:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance
    
    def __init__(self):
        if self.__initialized: return
        self.__initialized = True

        self.media_player = vlc.MediaPlayer()
        self.media_player.toggle_fullscreen()
        self.listen()
        # Thread(target=self.listen).start()

    def play_video(self, video_file):
        self.media_player.set_mrl(video_file)
        self.media_player.play()

    def listen(self):
        print("Client:","\tListening for incoming tcp messages")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((Config().MY_IP, Config().DATA_PORT))
            s.listen()
            start = time.perf_counter()
            while True:
                try:
                    conn, addr = s.accept()
                    with conn:
                        fragments = []
                        while True:
                            chunk = conn.recv(8096)
                            if not chunk:
                                break
                            fragments.append(chunk)
                        data = b''.join(fragments)
                        if not data:
                            continue
                        filename = f"{Config().TEMP_DIR}/{time.time()}{Config().FILE_EXTENSION}"
                        filetodown = open(filename, "wb")
                        filetodown.write(data)
                        filetodown.close()
                        self.play_video(filename)
                        print("It took", time.perf_counter()-start)
                        start = time.perf_counter()
                except Exception as e:
                    print("Client:","\tError in listening", e)
                    continue
