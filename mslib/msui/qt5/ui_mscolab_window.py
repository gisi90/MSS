# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mslib/msui/ui/ui_mscolab_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MSSMscolabWindow(object):
    def setupUi(self, MSSMscolabWindow):
        MSSMscolabWindow.setObjectName("MSSMscolabWindow")
        MSSMscolabWindow.resize(474, 380)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MSSMscolabWindow.sizePolicy().hasHeightForWidth())
        MSSMscolabWindow.setSizePolicy(sizePolicy)
        MSSMscolabWindow.setMinimumSize(QtCore.QSize(474, 380))
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(MSSMscolabWindow)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(0, 0, 471, 371))
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(self.verticalLayoutWidget_5)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loggedInWidget = QtWidgets.QWidget(self.groupBox)
        self.loggedInWidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loggedInWidget.sizePolicy().hasHeightForWidth())
        self.loggedInWidget.setSizePolicy(sizePolicy)
        self.loggedInWidget.setMinimumSize(QtCore.QSize(200, 40))
        self.loggedInWidget.setObjectName("loggedInWidget")
        self.horizontalLayoutWidget_4 = QtWidgets.QWidget(self.loggedInWidget)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(10, 10, 181, 31))
        self.horizontalLayoutWidget_4.setObjectName("horizontalLayoutWidget_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(300, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.logoutButton = QtWidgets.QPushButton(self.horizontalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logoutButton.sizePolicy().hasHeightForWidth())
        self.logoutButton.setSizePolicy(sizePolicy)
        self.logoutButton.setMinimumSize(QtCore.QSize(60, 0))
        self.logoutButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.logoutButton.setObjectName("logoutButton")
        self.horizontalLayout_4.addWidget(self.logoutButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout.addWidget(self.loggedInWidget)
        self.loginWidget = QtWidgets.QWidget(self.groupBox)
        self.loginWidget.setObjectName("loginWidget")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.loginWidget)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.emailid = QtWidgets.QLineEdit(self.loginWidget)
        self.emailid.setObjectName("emailid")
        self.horizontalLayout_3.addWidget(self.emailid)
        self.password = QtWidgets.QLineEdit(self.loginWidget)
        self.password.setObjectName("password")
        self.horizontalLayout_3.addWidget(self.password)
        self.loginButton = QtWidgets.QPushButton(self.loginWidget)
        self.loginButton.setObjectName("loginButton")
        self.horizontalLayout_3.addWidget(self.loginButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.addUser = QtWidgets.QPushButton(self.loginWidget)
        self.addUser.setMaximumSize(QtCore.QSize(80, 16777215))
        self.addUser.setObjectName("addUser")
        self.verticalLayout_5.addWidget(self.addUser)
        self.verticalLayout_8.addLayout(self.verticalLayout_5)
        self.verticalLayout.addWidget(self.loginWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.listProjects = QtWidgets.QListWidget(self.groupBox)
        self.listProjects.setAlternatingRowColors(False)
        self.listProjects.setTextElideMode(QtCore.Qt.ElideNone)
        self.listProjects.setObjectName("listProjects")
        self.horizontalLayout_2.addWidget(self.listProjects)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.addProject = QtWidgets.QPushButton(self.groupBox)
        self.addProject.setObjectName("addProject")
        self.verticalLayout_2.addWidget(self.addProject)
        self.export_2 = QtWidgets.QPushButton(self.groupBox)
        self.export_2.setObjectName("export_2")
        self.verticalLayout_2.addWidget(self.export_2)
        self.autoSave = QtWidgets.QCheckBox(self.groupBox)
        self.autoSave.setObjectName("autoSave")
        self.verticalLayout_2.addWidget(self.autoSave)
        self.save_ft = QtWidgets.QPushButton(self.groupBox)
        self.save_ft.setObjectName("save_ft")
        self.verticalLayout_2.addWidget(self.save_ft)
        self.fetch_ft = QtWidgets.QPushButton(self.groupBox)
        self.fetch_ft.setObjectName("fetch_ft")
        self.verticalLayout_2.addWidget(self.fetch_ft)
        self.autosaveStatus = QtWidgets.QLabel(self.groupBox)
        self.autosaveStatus.setText("")
        self.autosaveStatus.setObjectName("autosaveStatus")
        self.verticalLayout_2.addWidget(self.autosaveStatus)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableview = QtWidgets.QPushButton(self.groupBox)
        self.tableview.setObjectName("tableview")
        self.horizontalLayout.addWidget(self.tableview)
        self.sideview = QtWidgets.QPushButton(self.groupBox)
        self.sideview.setObjectName("sideview")
        self.horizontalLayout.addWidget(self.sideview)
        self.topview = QtWidgets.QPushButton(self.groupBox)
        self.topview.setObjectName("topview")
        self.horizontalLayout.addWidget(self.topview)
        self.projWindow = QtWidgets.QPushButton(self.groupBox)
        self.projWindow.setObjectName("projWindow")
        self.horizontalLayout.addWidget(self.projWindow)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_6.addLayout(self.verticalLayout_4)

        self.retranslateUi(MSSMscolabWindow)
        QtCore.QMetaObject.connectSlotsByName(MSSMscolabWindow)

    def retranslateUi(self, MSSMscolabWindow):
        _translate = QtCore.QCoreApplication.translate
        MSSMscolabWindow.setWindowTitle(_translate("MSSMscolabWindow", "Mscolab Create Projects"))
        self.groupBox.setTitle(_translate("MSSMscolabWindow", "Project listing"))
        self.label.setText(_translate("MSSMscolabWindow", "TextLabel"))
        self.logoutButton.setText(_translate("MSSMscolabWindow", "logout"))
        self.emailid.setPlaceholderText(_translate("MSSMscolabWindow", "emailid"))
        self.password.setPlaceholderText(_translate("MSSMscolabWindow", "password"))
        self.loginButton.setText(_translate("MSSMscolabWindow", "login"))
        self.addUser.setText(_translate("MSSMscolabWindow", "add user"))
        self.listProjects.setToolTip(_translate("MSSMscolabWindow", "List of mscolab projects."))
        self.addProject.setText(_translate("MSSMscolabWindow", "add project"))
        self.export_2.setText(_translate("MSSMscolabWindow", "export"))
        self.autoSave.setText(_translate("MSSMscolabWindow", "autosave"))
        self.save_ft.setText(_translate("MSSMscolabWindow", "save"))
        self.fetch_ft.setText(_translate("MSSMscolabWindow", "fetch"))
        self.tableview.setText(_translate("MSSMscolabWindow", "tableview"))
        self.sideview.setText(_translate("MSSMscolabWindow", "sideview"))
        self.topview.setText(_translate("MSSMscolabWindow", "topview"))
        self.projWindow.setText(_translate("MSSMscolabWindow", "chat window"))
