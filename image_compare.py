# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'image_compare.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from object_classfier import *
import cv2

class Ui_ImageCompare(object):
    strFirstImage = ''
    strSecondImage = ''

    def setupUi(self, ImageCompare):
        ImageCompare.setObjectName("BaseBall")
        ImageCompare.resize(871, 393)

        self.centralwidget = QtWidgets.QWidget(ImageCompare)
        self.centralwidget.setObjectName("centralwidget")

        self.input_group = QtWidgets.QGroupBox(self.centralwidget)
        self.input_group.setGeometry(QtCore.QRect(10, 7, 851, 351))
        self.input_group.setFlat(False)
        self.input_group.setCheckable(False)
        self.input_group.setObjectName("input_group")

        self.first_view = QtWidgets.QLabel(self.input_group)
        self.first_view.setGeometry(QtCore.QRect(10, 20, 411, 291))
        self.first_view.setFrameShape(QtWidgets.QFrame.Box)
        self.first_view.setText("")
        self.first_view.setObjectName("first_view")

        self.second_view = QtWidgets.QLabel(self.input_group)
        self.second_view.setGeometry(QtCore.QRect(430, 20, 411, 291))
        self.second_view.setFrameShape(QtWidgets.QFrame.Box)
        self.second_view.setText("")
        self.second_view.setObjectName("second_view")

        self.first_btn = QtWidgets.QPushButton(self.input_group)
        self.first_btn.setGeometry(QtCore.QRect(178, 320, 81, 23))
        self.first_btn.setObjectName("first_btn")
        self.first_btn.clicked.connect(self.onClickFirstBtn)

        self.second_btn = QtWidgets.QPushButton(self.input_group)
        self.second_btn.setGeometry(QtCore.QRect(598, 320, 81, 23))
        self.second_btn.setObjectName("second_btn")
        self.second_btn.clicked.connect(self.onClickSecondBtn)

        self.compare_btn = QtWidgets.QPushButton(self.centralwidget)
        self.compare_btn.setGeometry(QtCore.QRect(10, 364, 75, 23))
        self.compare_btn.setObjectName("compare_btn")
        self.compare_btn.clicked.connect(self.onClickCompareBtn)

        self.result_lbl = QtWidgets.QLabel(self.centralwidget)
        self.result_lbl.setGeometry(QtCore.QRect(110, 365, 251, 21))
        self.result_lbl.setObjectName("result_lbl")

        ImageCompare.setCentralWidget(self.centralwidget)

        self.retranslateUi(ImageCompare)
        QtCore.QMetaObject.connectSlotsByName(ImageCompare)

    def retranslateUi(self, ImageCompare):
        _translate = QtCore.QCoreApplication.translate
        ImageCompare.setWindowTitle(_translate("ImageCompare", "Image Comparing"))
        self.input_group.setTitle(_translate("ImageCompare", "Input"))
        self.first_btn.setText(_translate("ImageCompare", "First Image"))
        self.second_btn.setText(_translate("ImageCompare", "Second Image"))
        self.compare_btn.setText(_translate("ImageCompare", "Compare"))
        self.result_lbl.setText(_translate("ImageCompare", "Result : "))

    def onClickFirstBtn(self):
        self.strFirstImage = ''
        self.first_view.clear()
        self.strFirstImage = self.openFileNameDialog()
        if self.strFirstImage != '':
            pixmap = self.getShowImageData(self.strFirstImage)
            self.first_view.setPixmap(pixmap)
            self.first_view.setScaledContents(True)

    def onClickSecondBtn(self):
        self.strSecondImage = ''
        self.second_view.clear()
        self.strSecondImage = self.openFileNameDialog()
        if self.strSecondImage != '':
            pixmap = self.getShowImageData(self.strSecondImage)
            self.second_view.setPixmap(pixmap)
            self.second_view.setScaledContents(True)

    def onClickCompareBtn(self):
        if self.strFirstImage == '' or self.strSecondImage == '':
            self.informationDialog()
            return
        result = image_classfier(self.strFirstImage, self.strSecondImage)
        if result == None:
            result = 'Different Image'
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText('Processing State : ')
        msg.setInformativeText(result)
        msg.setWindowTitle('Processing State')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        self.result_lbl.setText(result)

    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        caption = 'Open Image'
        directory = ''
        filter = 'Image Files (*.jpg);;Image Files (*.png)'
        fileName = QtWidgets.QFileDialog.getOpenFileName(None, caption, directory, filter, options=options)
        return fileName[0]

    def getShowImageData(self, path):
        imageData = cv2.imread(path)
        imageData = cv2.cvtColor(imageData, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(imageData, imageData.shape[1], imageData.shape[0], imageData.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)

        pix = QtGui.QPixmap(image)
        return pix

    def informationDialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText('Don`t Ready Images for Comparing. : ')
        msg.setInformativeText('')
        msg.setWindowTitle('Information')
        msg.setDetailedText('Please Open First or Second Image.')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ImageCompare = QtWidgets.QMainWindow()
    ui = Ui_ImageCompare()
    ui.setupUi(ImageCompare)
    ImageCompare.show()
    sys.exit(app.exec_())

