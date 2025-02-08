# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vivi_deviceManager.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_device_manager(object):
    def setupUi(self, device_manager):
        if not device_manager.objectName():
            device_manager.setObjectName(u"device_manager")
        device_manager.resize(400, 278)
        self.verticalLayout = QVBoxLayout(device_manager)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_deviceName = QLabel(device_manager)
        self.label_deviceName.setObjectName(u"label_deviceName")

        self.verticalLayout.addWidget(self.label_deviceName)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.CB_deviceList = QComboBox(device_manager)
        self.CB_deviceList.setObjectName(u"CB_deviceList")

        self.horizontalLayout.addWidget(self.CB_deviceList)

        self.LE_addr = QLineEdit(device_manager)
        self.LE_addr.setObjectName(u"LE_addr")

        self.horizontalLayout.addWidget(self.LE_addr)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.CB_boardType = QComboBox(device_manager)
        self.CB_boardType.addItem("")
        self.CB_boardType.addItem("")
        self.CB_boardType.setObjectName(u"CB_boardType")

        self.horizontalLayout_2.addWidget(self.CB_boardType)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.PB_connect = QPushButton(device_manager)
        self.PB_connect.setObjectName(u"PB_connect")

        self.horizontalLayout_2.addWidget(self.PB_connect)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.PB_refresh = QPushButton(device_manager)
        self.PB_refresh.setObjectName(u"PB_refresh")

        self.horizontalLayout_2.addWidget(self.PB_refresh)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(device_manager)

        QMetaObject.connectSlotsByName(device_manager)
    # setupUi

    def retranslateUi(self, device_manager):
        device_manager.setWindowTitle(QCoreApplication.translate("device_manager", u"Form", None))
        self.label_deviceName.setText(QCoreApplication.translate("device_manager", u"TextLabel", None))
        self.CB_boardType.setItemText(0, QCoreApplication.translate("device_manager", u"ADC-8x", None))
        self.CB_boardType.setItemText(1, QCoreApplication.translate("device_manager", u"ADC-8", None))

        self.PB_connect.setText(QCoreApplication.translate("device_manager", u"Connect", None))
        self.PB_refresh.setText(QCoreApplication.translate("device_manager", u"Refresh", None))
    # retranslateUi

