# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vivi_adcSetting.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
    QLineEdit, QSizePolicy, QVBoxLayout, QWidget)

class Ui_adc_setting(object):
    def setupUi(self, adc_setting):
        if not adc_setting.objectName():
            adc_setting.setObjectName(u"adc_setting")
        adc_setting.resize(144, 179)
        self.horizontalLayout = QHBoxLayout(adc_setting)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.group_adc = QGroupBox(adc_setting)
        self.group_adc.setObjectName(u"group_adc")
        self.verticalLayout = QVBoxLayout(self.group_adc)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.LE_label = QLineEdit(self.group_adc)
        self.LE_label.setObjectName(u"LE_label")

        self.verticalLayout.addWidget(self.LE_label)

        self.CB_gain = QComboBox(self.group_adc)
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.setObjectName(u"CB_gain")

        self.verticalLayout.addWidget(self.CB_gain)


        self.horizontalLayout.addWidget(self.group_adc)


        self.retranslateUi(adc_setting)

        QMetaObject.connectSlotsByName(adc_setting)
    # setupUi

    def retranslateUi(self, adc_setting):
        adc_setting.setWindowTitle(QCoreApplication.translate("adc_setting", u"Form", None))
        self.group_adc.setTitle(QCoreApplication.translate("adc_setting", u"group_channel", None))
        self.LE_label.setText(QCoreApplication.translate("adc_setting", u"LE_label", None))
        self.CB_gain.setItemText(0, QCoreApplication.translate("adc_setting", u"128", None))
        self.CB_gain.setItemText(1, QCoreApplication.translate("adc_setting", u"64", None))
        self.CB_gain.setItemText(2, QCoreApplication.translate("adc_setting", u"32", None))
        self.CB_gain.setItemText(3, QCoreApplication.translate("adc_setting", u"16", None))
        self.CB_gain.setItemText(4, QCoreApplication.translate("adc_setting", u"8", None))
        self.CB_gain.setItemText(5, QCoreApplication.translate("adc_setting", u"1", None))
        self.CB_gain.setItemText(6, QCoreApplication.translate("adc_setting", u"Off", None))

    # retranslateUi

