import numpy as np
import cv2
from mss import mss
from PIL import Image
import time

bounding_box = {'top': 0, 'left': 0, 'width': 1000, 'height': 1000}

sct = mss()

while True:
    start = time.time()
    sct_img = sct.grab(bounding_box)
    cv2.imshow('screen', np.array(sct_img))

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break
    end = time.time()
    print(end - start)