# importing the required packages
import os
from threading import Thread
import time

import cv2
import numpy as np
from mss import mss

from config import Config
from utils import compress_video
from utils.perfect_sleep import perfect_sleep
import multiprocessing as mp
from queue import Queue

from saver import saver

def record(fps = Config().VIDEO_FPS):
	filename = f"{Config().TEMP_DIR}/{time.time()}{Config().FILE_EXTENSION}"
	
	# out: cv2.VideoWriter = cv2.VideoWriter(filename, Config().VIDEO_CODEC, fps, Config().VIDEO_RESOLUTION)
	sct = mss()
	bounding_box = {'top': 0, 'left': 0, 'width': Config().VIDEO_RESOLUTION[0], 'height': Config().VIDEO_RESOLUTION[1]}
	
	counter = 0

	first_time = time.perf_counter()
	# q = mp.Queue()
	q= Queue()
	process = Thread(target=saver, args=(q, filename))
	process.start()
	while True:
		if(counter == Config().VIDEO_DURATION * fps): break
		counter += 1

		frame_start_time = time.perf_counter()
		sct_img = sct.grab(bounding_box)
		sct_img = np.array(sct_img, dtype=np.uint8)

		frame = cv2.cvtColor(sct_img, cv2.COLOR_RGB2BGR)
		q.put(frame)
		# out.write(frame)

		frame_duration = time.perf_counter() - frame_start_time
		perfect_sleep(1/fps - frame_duration)
	q.put(None)
	# process.join()
	# out.write(np.array(outs))
	# out.release()
	if Config().COMPRESSION_ENABLED: filencxame = compress_video.compress(filename)

	# print(f"Compression took {time.perf_counter() - s} seconds")
	print(f"Total time elapsed: {time.perf_counter() - first_time} seconds")
	# print(f"file size: {os.path.getsize(filename)/1024/1024} mb")
	return filename