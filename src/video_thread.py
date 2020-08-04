# import necessary packages
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal # in case of erros, add: from PyQt5.QtCore import * 
import imutils

# VideoThread class for updating frames
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.cap = False

    def run(self):
        # capture from web cam
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while self._run_flag:
            ret, cv_img = self.cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)

    def stop(self):
        # shut down capture system
        self.cap.release()
        self._run_flag = False
        self.wait()
