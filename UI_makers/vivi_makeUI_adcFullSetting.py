# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vivi_adcFullSetting.ui'
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
    QLabel, QSizePolicy, QVBoxLayout, QWidget)

class Ui_adc_full_setting(object):
    def setupUi(self, adc_full_setting):
        if not adc_full_setting.objectName():
            adc_full_setting.setObjectName(u"adc_full_setting")
        adc_full_setting.resize(251, 226)
        self.verticalLayout = QVBoxLayout(adc_full_setting)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(adc_full_setting)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)

        self.widget_gain = QWidget(self.groupBox)
        self.widget_gain.setObjectName(u"widget_gain")
        self.layout_gain = QHBoxLayout(self.widget_gain)
        self.layout_gain.setObjectName(u"layout_gain")
        self.label_2 = QLabel(self.widget_gain)
        self.label_2.setObjectName(u"label_2")

        self.layout_gain.addWidget(self.label_2)

        self.CB_gain = QComboBox(self.widget_gain)
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.addItem("")
        self.CB_gain.setObjectName(u"CB_gain")

        self.layout_gain.addWidget(self.CB_gain)


        self.verticalLayout_2.addWidget(self.widget_gain)

        self.widget_polarity = QWidget(self.groupBox)
        self.widget_polarity.setObjectName(u"widget_polarity")
        self.layout_polarity = QHBoxLayout(self.widget_polarity)
        self.layout_polarity.setObjectName(u"layout_polarity")
        self.label_3 = QLabel(self.widget_polarity)
        self.label_3.setObjectName(u"label_3")

        self.layout_polarity.addWidget(self.label_3)

        self.CB_polarity = QComboBox(self.widget_polarity)
        self.CB_polarity.addItem("")
        self.CB_polarity.addItem("")
        self.CB_polarity.setObjectName(u"CB_polarity")

        self.layout_polarity.addWidget(self.CB_polarity)


        self.verticalLayout_2.addWidget(self.widget_polarity)

        self.widget_buffer = QWidget(self.groupBox)
        self.widget_buffer.setObjectName(u"widget_buffer")
        self.layout_buffer = QHBoxLayout(self.widget_buffer)
        self.layout_buffer.setObjectName(u"layout_buffer")
        self.label_4 = QLabel(self.widget_buffer)
        self.label_4.setObjectName(u"label_4")

        self.layout_buffer.addWidget(self.label_4)

        self.CB_buffer = QComboBox(self.widget_buffer)
        self.CB_buffer.addItem("")
        self.CB_buffer.addItem("")
        self.CB_buffer.setObjectName(u"CB_buffer")

        self.layout_buffer.addWidget(self.CB_buffer)


        self.verticalLayout_2.addWidget(self.widget_buffer)

        self.widget_impedance = QWidget(self.groupBox)
        self.widget_impedance.setObjectName(u"widget_impedance")
        self.layout_sensor = QHBoxLayout(self.widget_impedance)
        self.layout_sensor.setObjectName(u"layout_sensor")
        self.label_5 = QLabel(self.widget_impedance)
        self.label_5.setObjectName(u"label_5")

        self.layout_sensor.addWidget(self.label_5)

        self.CB_impedance = QComboBox(self.widget_impedance)
        self.CB_impedance.addItem("")
        self.CB_impedance.addItem("")
        self.CB_impedance.setObjectName(u"CB_impedance")

        self.layout_sensor.addWidget(self.CB_impedance)


        self.verticalLayout_2.addWidget(self.widget_impedance)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(adc_full_setting)

        QMetaObject.connectSlotsByName(adc_full_setting)
    # setupUi

    def retranslateUi(self, adc_full_setting):
        adc_full_setting.setWindowTitle(QCoreApplication.translate("adc_full_setting", u"Form", None))
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("adc_full_setting", u"Ch 1", None))
        self.label_2.setText(QCoreApplication.translate("adc_full_setting", u"Gain:", None))
        self.CB_gain.setItemText(0, QCoreApplication.translate("adc_full_setting", u"128", None))
        self.CB_gain.setItemText(1, QCoreApplication.translate("adc_full_setting", u"64", None))
        self.CB_gain.setItemText(2, QCoreApplication.translate("adc_full_setting", u"32", None))
        self.CB_gain.setItemText(3, QCoreApplication.translate("adc_full_setting", u"16", None))
        self.CB_gain.setItemText(4, QCoreApplication.translate("adc_full_setting", u"8", None))
        self.CB_gain.setItemText(5, QCoreApplication.translate("adc_full_setting", u"1", None))
        self.CB_gain.setItemText(6, QCoreApplication.translate("adc_full_setting", u"Off", None))

        self.label_3.setText(QCoreApplication.translate("adc_full_setting", u"Polarity:", None))
        self.CB_polarity.setItemText(0, QCoreApplication.translate("adc_full_setting", u"Unipolar", None))
        self.CB_polarity.setItemText(1, QCoreApplication.translate("adc_full_setting", u"Bipolar", None))

        self.label_4.setText(QCoreApplication.translate("adc_full_setting", u"Buffer:", None))
        self.CB_buffer.setItemText(0, QCoreApplication.translate("adc_full_setting", u"Buffered", None))
        self.CB_buffer.setItemText(1, QCoreApplication.translate("adc_full_setting", u"Unbuffered", None))

        self.label_5.setText(QCoreApplication.translate("adc_full_setting", u"Impedence", None))
        self.CB_impedance.setItemText(0, QCoreApplication.translate("adc_full_setting", u"+", None))
        self.CB_impedance.setItemText(1, QCoreApplication.translate("adc_full_setting", u"-", None))

    # retranslateUi

