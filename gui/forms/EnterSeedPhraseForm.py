# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EnterSeedPhrase.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(450, 220)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(0, 0))
        Form.setMaximumSize(QtCore.QSize(400000, 555555))
        self.seedTextEdit = QtWidgets.QPlainTextEdit(Form)
        self.seedTextEdit.setGeometry(QtCore.QRect(10, 10, 430, 130))
        self.seedTextEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.seedTextEdit.setInputMethodHints(QtCore.Qt.ImhMultiLine)
        self.seedTextEdit.setTabChangesFocus(False)
        self.seedTextEdit.setUndoRedoEnabled(True)
        self.seedTextEdit.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        self.seedTextEdit.setPlainText("")
        self.seedTextEdit.setOverwriteMode(False)
        self.seedTextEdit.setBackgroundVisible(False)
        self.seedTextEdit.setCenterOnScroll(False)
        self.seedTextEdit.setObjectName("seedTextEdit")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 170, 231, 35))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.nextButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.nextButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.nextButton.setFont(font)
        self.nextButton.setAutoDefault(False)
        self.nextButton.setDefault(False)
        self.nextButton.setFlat(False)
        self.nextButton.setObjectName("nextButton")
        self.horizontalLayout.addWidget(self.nextButton)
        self.exitButton = QtWidgets.QPushButton(Form)
        self.exitButton.setGeometry(QtCore.QRect(350, 170, 93, 33))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.exitButton.setFont(font)
        self.exitButton.setObjectName("exitButton")
        self.labelValid = QtWidgets.QLabel(Form)
        self.labelValid.setGeometry(QtCore.QRect(250, 148, 191, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.labelValid.setFont(font)
        self.labelValid.setText("")
        self.labelValid.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelValid.setObjectName("labelValid")

        self.retranslateUi(Form)
        self.cancelButton.pressed.connect(Form.cancelButtonPressed) # type: ignore
        self.nextButton.pressed.connect(Form.nextButtonPressed) # type: ignore
        self.exitButton.pressed.connect(Form.exitButtonPressed) # type: ignore
        self.seedTextEdit.textChanged.connect(Form.textEditTextChanged) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "SPMC"))
        self.seedTextEdit.setPlaceholderText(_translate("Form", "Please enter the seed phrase it should consist of 3, 6, 9, 12, 15, 18, 21 or 24 words, according to the dictionary from bip39"))
        self.cancelButton.setText(_translate("Form", "cancel"))
        self.nextButton.setText(_translate("Form", "next"))
        self.exitButton.setText(_translate("Form", "exit"))
