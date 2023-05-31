from __future__ import annotations

import time
from threading import Thread

from utils.send_packet import send_packet

from config import Config
from utils import video_recorder,perfect_sleep, compress_video
from connection import Connection
from itertools import combinations

from sympy import symbols, Eq, solve

class SyncManager:
    current_delays = {}
    equations = {}

    def solve(self):
        try:
            clients = sorted(Connection().connected_ips.inv.keys())
            clients.append('server')
            if(len(clients) < 3):
                print('SyncManager solve error: Not enough clients to solve sync equations')
                return 
            temp = {}
            for k,v in SyncManager().equations.items():
                if('server' in k and k[0] != clients[0]): continue
                if(len(v) == 0):
                    temp[k] = 0
                else:
                    temp[k] = sum([float(m) for m in v])/len(v)            
            
            for k in self.equations.keys():
                self.equations[k].clear()

            s = symbols(' '.join(clients))
            symbol_dict = {x: s[i] for i,x in enumerate(clients)}

            eqs = []
            for k,v in temp.items():    
                eqs.append(Eq(symbol_dict[k[0]] + symbol_dict[k[1]],v))
            
            solv = solve(eqs, s)
            if(len(solv) == 0):
                print('SyncManager solve error: No solution found')
                return

            delays = {x: solv[symbol_dict[x]] for x in clients}
            # delays['c3']= 1000

            m = min(delays.values())

            if(m < 0):
                for i,k in enumerate(delays.keys()):
                    delays[k] -= m

            self.current_delays = dict(sorted(delays.items(), key=lambda x: x[1], reverse=True))

            print(self.current_delays)
        except Exception as e:
            print('SyncManager solve error', e)

    
    def update(self, sender_name: str, receiver_name: str, delay:float,):
        print(f"SyncManager: {sender_name} -> {receiver_name} = {delay} ms")
        current_clients = sorted(Connection().connected_ips.inv.keys())
        current_clients.append('server')

        current_combs = combinations(current_clients, 2)
        new_comers = set(current_combs) - set(self.equations.keys())

        for new_comer_tuple in new_comers:
            self.equations[new_comer_tuple] = []
            for c in new_comer_tuple:
                self.current_delays[c] = 0


        naming_tuple = (sender_name, receiver_name) if sender_name < receiver_name else (receiver_name, sender_name)
        if naming_tuple not in self.equations:
            self.equations[naming_tuple] = []
        self.equations[naming_tuple].append(delay)


class Server:
    last = time.perf_counter()
    currently_recording = False
    syncManager = SyncManager()
    
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
            if Config().COMPRESSION_ENABLED: recorded_file =compress_video.get_compress_name(recorded_file)
            Thread(target=Server().send_video_to_users, args=(recorded_file,)).start()
            
            
    def send_video_to_users(self, recorded_file):
        time.sleep(0.5)
        print(time.perf_counter()-Server().last)
        Server().last = time.perf_counter()

        f = open(recorded_file, 'rb')
        file_bytes = f.read()
        f.close()

        previous_delay = 0
        for client in Server().syncManager.current_delays.keys():
            if client == 'server': continue
            delay = previous_delay - Server().syncManager.current_delays[client]
            previous_delay = Server().syncManager.current_delays[client]
            perfect_sleep.perfect_sleep(max(0, delay/1000))
            send_packet(Connection().connected_ips.inv[client], Config().DATA_PORT, file_bytes)

    def stop_recording(self):
        self.currently_recording = False
