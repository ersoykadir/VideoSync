import cv2


def saver(queue, filename):
	print("BELOOOOO")
	VIDEO_CODEC = cv2.VideoWriter_fourcc(*"avc1")
	VIDEO_FPS = 30
	VIDEO_RESOLUTION = (1000, 1000)
	out = cv2.VideoWriter(filename, VIDEO_CODEC, VIDEO_FPS, VIDEO_RESOLUTION)
	while True:
		frame = queue.get()
		if frame is None: break
		out.write(frame)
	out.release()