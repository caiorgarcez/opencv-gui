
# opencv-GUI
# import Pyqt5 necessary packages
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow,  QWidget, QApplication, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUiType

# general python packages
import sys
import os
from os import path
import numpy as np
import cv2
import imutils
from imutils import paths, face_utils
import requests
import time
from datetime import datetime
import pickle
import face_recognition
import sqlite3
from contextlib import contextmanager

# custom threads for video stream
from src.video_thread import VideoThread
# from src.recon_thread import ReconThread

# create a resource path to handle with pyinstaller tmp dir to build the application
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# load UI from QtDesigner
FORM_CLASS, _ = loadUiType(resource_path("main.ui"))

# define a context manager to manage users database
@contextmanager
def connect_database():
    global conn
    conn = sqlite3.connect(resource_path("database.db"))
    try:
        yield conn
    finally:
        conn.close()

# PyQt5 main window
class Main(QMainWindow, FORM_CLASS):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        # load custon Ui from QtDesigner
        self.setupUi(self)
        self.setWindowTitle("Opencv-based Application")

        # define frame capture and labels dimensions for cv2.imshow() set to labels
        self.display_width = 500
        self.display_height = 500

        self.webcam_lbl.resize(self.display_width, self.display_height)
        # self.label_11.resize(self.display_width, self.display_height)

        # order tabs to be shown when starting the application
        self.homeTab.hide()
        self.registerTab.hide()
        
        # hide intermediate labels
        self.successRegister.hide()

        # connect pushbuttons to run threads
        self.loginButton.clicked.connect(self.handleLogin)        
        self.backLogin.clicked.connect(self.backtoLogin)
        self.backLogin_2.clicked.connect(self.backtoLogin)
        self.newUserButton.clicked.connect(self.loadRegister)
        self.registerButton.clicked.connect(self.register)

    # navigate to register page
    def loadRegister(self):
        self.loginTab.hide()
        self.registerTab.show()
        
    # register new users
    def register(self):
        global conn
        if self.username_led_reg.text() == "":
            input1 = False
            QMessageBox.warning(self, 'Error', 'Username field is empty')
        else: 
            name = self.username_led_reg.text()
            input1 = True

        if self.password_led_reg1.text() == self.password_led_reg2.text():
            password = self.password_led_reg1.text()
            input2 = True
        else:
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            input2 = False

        # case the entry is valid insert the new user to database
        if input1 and input2:
            with connect_database() as database:
                cursor = database.cursor()
                command = 'INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)'
                cursor.execute(command, (name, password))
                database.commit()
                cursor.close()

            # hide labels
            self.registerButton.hide()
            self.usarname_login_3.hide()
            self.password_login_3.hide()
            self.password_login_6.hide()
            self.username_led_reg.hide()
            self.password_led_reg1.hide()
            self.password_led_reg2.hide()
            self.successRegister.show()

    # process login 
    def handleLogin(self):
        logged = False

        # check the database for matching credentials
        with connect_database() as database:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM users ORDER BY id ASC')
            res = cursor.fetchall()
            for ln in res:
                if self.username_led.text() == ln[1] and self.password_led.text() == ln[2]:
                    
                    # authorized user
                    logged = True

                    # load home screen
                    self.loginTab.hide()
                    self.homeTab.show()
                    self.startThread()

            if not logged:
                QMessageBox.warning(self, 'Error', 'Bad username or password')
            cursor.close()

    # navigate back to login screen
    def backtoLogin(self):
        # load login screen and clear linedit inputs
        self.homeTab.hide()
        self.registerTab.hide()
        self.loginTab.show()
        self.username_led.setText("")
        self.password_led.setText("")

    def startThread(self):
        # create the video capture thread connect its signal and run
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        # display frames
        self.webcam_lbl.show()

    def closeEvent(self, event):
        # stop threads before closing
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    # updates the image_label with a new opencv image
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.webcam_lbl.setPixmap(qt_img)
    
    # convert from an opencv image to QPixmap
    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

# start PyQt5 application
def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()

# run the application for the main file
if __name__ == '__main__':
    main()