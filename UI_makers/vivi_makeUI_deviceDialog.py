# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vivi_deviceDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_device_dialog(object):
    def setupUi(self, device_dialog):
        if not device_dialog.objectName():
            device_dialog.setObjectName(u"device_dialog")
        device_dialog.resize(740, 373)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(device_dialog.sizePolicy().hasHeightForWidth())
        device_dialog.setSizePolicy(sizePolicy)
        device_dialog.setMinimumSize(QSize(740, 373))
        self.horizontalLayout = QHBoxLayout(device_dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.group_logo = QGroupBox(device_dialog)
        self.group_logo.setObjectName(u"group_logo")
        self.group_logo.setFlat(True)

        self.horizontalLayout.addWidget(self.group_logo)

        self.group_dev = QGroupBox(device_dialog)
        self.group_dev.setObjectName(u"group_dev")
        self.group_dev.setFlat(True)
        self.layout_dev = QVBoxLayout(self.group_dev)
        self.layout_dev.setSpacing(12)
        self.layout_dev.setObjectName(u"layout_dev")
        self.layout_dev.setContentsMargins(0, 0, 0, 0)
        self.PB_start_main = QPushButton(self.group_dev)
        self.PB_start_main.setObjectName(u"PB_start_main")

        self.layout_dev.addWidget(self.PB_start_main, 0, Qt.AlignHCenter)


        self.horizontalLayout.addWidget(self.group_dev)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)

        self.retranslateUi(device_dialog)

        QMetaObject.connectSlotsByName(device_dialog)
    # setupUi

    def retranslateUi(self, device_dialog):
        device_dialog.setWindowTitle(QCoreApplication.translate("device_dialog", u"Form", None))
        self.group_logo.setTitle("")
        self.group_dev.setTitle("")
        self.PB_start_main.setText(QCoreApplication.translate("device_dialog", u"Start Vivi", None))
    # retranslateUi

