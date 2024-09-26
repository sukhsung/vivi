# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vivi.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 720)
        MainWindow.setMinimumSize(QSize(1280, 718))
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.group_left = QGroupBox(self.centralwidget)
        self.group_left.setObjectName(u"group_left")
        self.layout_left = QVBoxLayout(self.group_left)
        self.layout_left.setObjectName(u"layout_left")
        self.layout_left.setContentsMargins(12, 12, 12, 12)
        self.group_device = QGroupBox(self.group_left)
        self.group_device.setObjectName(u"group_device")
        self.group_device.setFlat(False)
        self.verticalLayout_2 = QVBoxLayout(self.group_device)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.layout_device = QHBoxLayout()
        self.layout_device.setObjectName(u"layout_device")
        self.dev_list = QComboBox(self.group_device)
        self.dev_list.setObjectName(u"dev_list")

        self.layout_device.addWidget(self.dev_list)

        self.LE_URL = QLineEdit(self.group_device)
        self.LE_URL.setObjectName(u"LE_URL")
        self.LE_URL.setMinimumSize(QSize(80, 0))

        self.layout_device.addWidget(self.LE_URL)

        self.PB_connect = QPushButton(self.group_device)
        self.PB_connect.setObjectName(u"PB_connect")

        self.layout_device.addWidget(self.PB_connect)

        self.PB_refresh = QPushButton(self.group_device)
        self.PB_refresh.setObjectName(u"PB_refresh")

        self.layout_device.addWidget(self.PB_refresh)


        self.verticalLayout_2.addLayout(self.layout_device)

        self.group_device_setting = QGroupBox(self.group_device)
        self.group_device_setting.setObjectName(u"group_device_setting")
        self.group_device_setting.setFlat(True)
        self.verticalLayout_3 = QVBoxLayout(self.group_device_setting)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.group_allgain = QGroupBox(self.group_device_setting)
        self.group_allgain.setObjectName(u"group_allgain")
        self.group_allgain.setFlat(True)
        self.horizontalLayout_14 = QHBoxLayout(self.group_allgain)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(12, 0, 0, 0)
        self.label = QLabel(self.group_allgain)
        self.label.setObjectName(u"label")

        self.horizontalLayout_14.addWidget(self.label)

        self.CB_allGains = QComboBox(self.group_allgain)
        self.CB_allGains.setObjectName(u"CB_allGains")
        self.CB_allGains.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_14.addWidget(self.CB_allGains)


        self.horizontalLayout_3.addWidget(self.group_allgain)

        self.group_sampling = QGroupBox(self.group_device_setting)
        self.group_sampling.setObjectName(u"group_sampling")
        self.group_sampling.setFlat(True)
        self.horizontalLayout_15 = QHBoxLayout(self.group_sampling)
        self.horizontalLayout_15.setSpacing(0)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.group_sampling)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_15.addWidget(self.label_2)

        self.TB_sampling = QLineEdit(self.group_sampling)
        self.TB_sampling.setObjectName(u"TB_sampling")
        self.TB_sampling.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_15.addWidget(self.TB_sampling)


        self.horizontalLayout_3.addWidget(self.group_sampling)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(6)
        self.gridLayout_2.setVerticalSpacing(20)
        self.group_channel_8 = QGroupBox(self.group_device_setting)
        self.group_channel_8.setObjectName(u"group_channel_8")
        self.group_channel_8.setMaximumSize(QSize(85, 16777215))
        self.group_channel_8.setFlat(False)
        self.verticalLayout_10 = QVBoxLayout(self.group_channel_8)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_8 = QComboBox(self.group_channel_8)
        self.CB_gain_8.setObjectName(u"CB_gain_8")

        self.verticalLayout_10.addWidget(self.CB_gain_8)

        self.TB_gains_label_8 = QLineEdit(self.group_channel_8)
        self.TB_gains_label_8.setObjectName(u"TB_gains_label_8")

        self.verticalLayout_10.addWidget(self.TB_gains_label_8)


        self.gridLayout_2.addWidget(self.group_channel_8, 1, 3, 1, 1)

        self.group_channel_6 = QGroupBox(self.group_device_setting)
        self.group_channel_6.setObjectName(u"group_channel_6")
        self.group_channel_6.setMaximumSize(QSize(85, 16777215))
        self.group_channel_6.setFlat(False)
        self.verticalLayout_6 = QVBoxLayout(self.group_channel_6)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_6 = QComboBox(self.group_channel_6)
        self.CB_gain_6.setObjectName(u"CB_gain_6")

        self.verticalLayout_6.addWidget(self.CB_gain_6)

        self.TB_gains_label_6 = QLineEdit(self.group_channel_6)
        self.TB_gains_label_6.setObjectName(u"TB_gains_label_6")

        self.verticalLayout_6.addWidget(self.TB_gains_label_6)


        self.gridLayout_2.addWidget(self.group_channel_6, 1, 1, 1, 1)

        self.group_channel_7 = QGroupBox(self.group_device_setting)
        self.group_channel_7.setObjectName(u"group_channel_7")
        self.group_channel_7.setMaximumSize(QSize(85, 16777215))
        self.group_channel_7.setFlat(False)
        self.verticalLayout_8 = QVBoxLayout(self.group_channel_7)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_7 = QComboBox(self.group_channel_7)
        self.CB_gain_7.setObjectName(u"CB_gain_7")

        self.verticalLayout_8.addWidget(self.CB_gain_7)

        self.TB_gains_label_7 = QLineEdit(self.group_channel_7)
        self.TB_gains_label_7.setObjectName(u"TB_gains_label_7")

        self.verticalLayout_8.addWidget(self.TB_gains_label_7)


        self.gridLayout_2.addWidget(self.group_channel_7, 1, 2, 1, 1)

        self.group_channel_3 = QGroupBox(self.group_device_setting)
        self.group_channel_3.setObjectName(u"group_channel_3")
        self.group_channel_3.setMaximumSize(QSize(85, 16777215))
        self.group_channel_3.setFlat(False)
        self.verticalLayout_9 = QVBoxLayout(self.group_channel_3)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_3 = QComboBox(self.group_channel_3)
        self.CB_gain_3.setObjectName(u"CB_gain_3")

        self.verticalLayout_9.addWidget(self.CB_gain_3)

        self.TB_gains_label_3 = QLineEdit(self.group_channel_3)
        self.TB_gains_label_3.setObjectName(u"TB_gains_label_3")

        self.verticalLayout_9.addWidget(self.TB_gains_label_3)


        self.gridLayout_2.addWidget(self.group_channel_3, 0, 2, 1, 1)

        self.group_channel_4 = QGroupBox(self.group_device_setting)
        self.group_channel_4.setObjectName(u"group_channel_4")
        self.group_channel_4.setMaximumSize(QSize(85, 16777215))
        self.group_channel_4.setFlat(False)
        self.verticalLayout_11 = QVBoxLayout(self.group_channel_4)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_4 = QComboBox(self.group_channel_4)
        self.CB_gain_4.setObjectName(u"CB_gain_4")

        self.verticalLayout_11.addWidget(self.CB_gain_4)

        self.TB_gains_label_4 = QLineEdit(self.group_channel_4)
        self.TB_gains_label_4.setObjectName(u"TB_gains_label_4")

        self.verticalLayout_11.addWidget(self.TB_gains_label_4)


        self.gridLayout_2.addWidget(self.group_channel_4, 0, 3, 1, 1)

        self.group_channel_2 = QGroupBox(self.group_device_setting)
        self.group_channel_2.setObjectName(u"group_channel_2")
        self.group_channel_2.setMaximumSize(QSize(85, 16777215))
        self.group_channel_2.setFlat(False)
        self.verticalLayout_5 = QVBoxLayout(self.group_channel_2)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_2 = QComboBox(self.group_channel_2)
        self.CB_gain_2.setObjectName(u"CB_gain_2")

        self.verticalLayout_5.addWidget(self.CB_gain_2)

        self.TB_gains_label_2 = QLineEdit(self.group_channel_2)
        self.TB_gains_label_2.setObjectName(u"TB_gains_label_2")

        self.verticalLayout_5.addWidget(self.TB_gains_label_2)


        self.gridLayout_2.addWidget(self.group_channel_2, 0, 1, 1, 1)

        self.group_channel_1 = QGroupBox(self.group_device_setting)
        self.group_channel_1.setObjectName(u"group_channel_1")
        self.group_channel_1.setMaximumSize(QSize(85, 16777215))
        self.group_channel_1.setFlat(False)
        self.verticalLayout_7 = QVBoxLayout(self.group_channel_1)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_1 = QComboBox(self.group_channel_1)
        self.CB_gain_1.setObjectName(u"CB_gain_1")

        self.verticalLayout_7.addWidget(self.CB_gain_1)

        self.TB_gains_label_1 = QLineEdit(self.group_channel_1)
        self.TB_gains_label_1.setObjectName(u"TB_gains_label_1")

        self.verticalLayout_7.addWidget(self.TB_gains_label_1)


        self.gridLayout_2.addWidget(self.group_channel_1, 0, 0, 1, 1)

        self.group_channel_5 = QGroupBox(self.group_device_setting)
        self.group_channel_5.setObjectName(u"group_channel_5")
        self.group_channel_5.setMaximumSize(QSize(85, 16777215))
        self.group_channel_5.setFlat(False)
        self.verticalLayout_4 = QVBoxLayout(self.group_channel_5)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.CB_gain_5 = QComboBox(self.group_channel_5)
        self.CB_gain_5.setObjectName(u"CB_gain_5")

        self.verticalLayout_4.addWidget(self.CB_gain_5)

        self.TB_gains_label_5 = QLineEdit(self.group_channel_5)
        self.TB_gains_label_5.setObjectName(u"TB_gains_label_5")

        self.verticalLayout_4.addWidget(self.TB_gains_label_5)


        self.gridLayout_2.addWidget(self.group_channel_5, 1, 0, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_2)


        self.verticalLayout_2.addWidget(self.group_device_setting)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 3)

        self.layout_left.addWidget(self.group_device)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_left.addItem(self.verticalSpacer_2)

        self.group_cmd = QGroupBox(self.group_left)
        self.group_cmd.setObjectName(u"group_cmd")
        self.verticalLayout_16 = QVBoxLayout(self.group_cmd)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer)

        self.PB_closeCMD = QPushButton(self.group_cmd)
        self.PB_closeCMD.setObjectName(u"PB_closeCMD")

        self.horizontalLayout_13.addWidget(self.PB_closeCMD)


        self.verticalLayout_16.addLayout(self.horizontalLayout_13)

        self.TE_deviceStatus = QTextEdit(self.group_cmd)
        self.TE_deviceStatus.setObjectName(u"TE_deviceStatus")

        self.verticalLayout_16.addWidget(self.TE_deviceStatus)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.LE_command = QLineEdit(self.group_cmd)
        self.LE_command.setObjectName(u"LE_command")

        self.horizontalLayout_12.addWidget(self.LE_command)

        self.PB_send = QPushButton(self.group_cmd)
        self.PB_send.setObjectName(u"PB_send")

        self.horizontalLayout_12.addWidget(self.PB_send)

        self.PB_clear = QPushButton(self.group_cmd)
        self.PB_clear.setObjectName(u"PB_clear")

        self.horizontalLayout_12.addWidget(self.PB_clear)


        self.verticalLayout_16.addLayout(self.horizontalLayout_12)


        self.layout_left.addWidget(self.group_cmd)

        self.group_logo = QGroupBox(self.group_left)
        self.group_logo.setObjectName(u"group_logo")
        self.group_logo.setMinimumSize(QSize(0, 400))
        self.group_logo.setAlignment(Qt.AlignCenter)
        self.group_logo.setFlat(True)
        self.layout_logo = QVBoxLayout(self.group_logo)
        self.layout_logo.setObjectName(u"layout_logo")
        self.layout_logo.setContentsMargins(0, 0, 0, 0)

        self.layout_left.addWidget(self.group_logo)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_left.addItem(self.verticalSpacer)

        self.layout_left.setStretch(0, 1)
        self.layout_left.setStretch(4, 1)

        self.horizontalLayout.addWidget(self.group_left)

        self.group_viviewer = QGroupBox(self.centralwidget)
        self.group_viviewer.setObjectName(u"group_viviewer")
        self.verticalLayout_12 = QVBoxLayout(self.group_viviewer)
        self.verticalLayout_12.setSpacing(12)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(12, 12, 12, 12)
        self.group_viewer = QGroupBox(self.group_viviewer)
        self.group_viewer.setObjectName(u"group_viewer")
        self.group_viewer.setFlat(False)
        self.horizontalLayout_5 = QHBoxLayout(self.group_viewer)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.groupBox_10 = QGroupBox(self.group_viewer)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.groupBox_10.setFlat(True)
        self.verticalLayout_15 = QVBoxLayout(self.groupBox_10)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.group_live_control = QGroupBox(self.groupBox_10)
        self.group_live_control.setObjectName(u"group_live_control")
        self.group_live_control.setFlat(True)
        self.verticalLayout_13 = QVBoxLayout(self.group_live_control)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.PB_live_start = QPushButton(self.group_live_control)
        self.PB_live_start.setObjectName(u"PB_live_start")

        self.verticalLayout_13.addWidget(self.PB_live_start)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_5 = QLabel(self.group_live_control)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_6.addWidget(self.label_5)

        self.LE_num_live_sample = QLineEdit(self.group_live_control)
        self.LE_num_live_sample.setObjectName(u"LE_num_live_sample")
        self.LE_num_live_sample.setMinimumSize(QSize(35, 0))

        self.horizontalLayout_6.addWidget(self.LE_num_live_sample)


        self.verticalLayout_13.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_6 = QLabel(self.group_live_control)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_7.addWidget(self.label_6)

        self.LE_num_dft_live = QLineEdit(self.group_live_control)
        self.LE_num_dft_live.setObjectName(u"LE_num_dft_live")

        self.horizontalLayout_7.addWidget(self.LE_num_dft_live)


        self.verticalLayout_13.addLayout(self.horizontalLayout_7)

        self.CheckBox_average = QCheckBox(self.group_live_control)
        self.CheckBox_average.setObjectName(u"CheckBox_average")

        self.verticalLayout_13.addWidget(self.CheckBox_average)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.CB_plot_4 = QCheckBox(self.group_live_control)
        self.CB_plot_4.setObjectName(u"CB_plot_4")
        font = QFont()
        font.setKerning(True)
        self.CB_plot_4.setFont(font)

        self.gridLayout_4.addWidget(self.CB_plot_4, 0, 3, 1, 1)

        self.CB_plot_3 = QCheckBox(self.group_live_control)
        self.CB_plot_3.setObjectName(u"CB_plot_3")

        self.gridLayout_4.addWidget(self.CB_plot_3, 0, 2, 1, 1)

        self.CB_plot_2 = QCheckBox(self.group_live_control)
        self.CB_plot_2.setObjectName(u"CB_plot_2")

        self.gridLayout_4.addWidget(self.CB_plot_2, 0, 1, 1, 1)

        self.CB_plot_1 = QCheckBox(self.group_live_control)
        self.CB_plot_1.setObjectName(u"CB_plot_1")

        self.gridLayout_4.addWidget(self.CB_plot_1, 0, 0, 1, 1)

        self.CB_plot_5 = QCheckBox(self.group_live_control)
        self.CB_plot_5.setObjectName(u"CB_plot_5")

        self.gridLayout_4.addWidget(self.CB_plot_5, 1, 0, 1, 1)

        self.CB_plot_6 = QCheckBox(self.group_live_control)
        self.CB_plot_6.setObjectName(u"CB_plot_6")

        self.gridLayout_4.addWidget(self.CB_plot_6, 1, 1, 1, 1)

        self.CB_plot_7 = QCheckBox(self.group_live_control)
        self.CB_plot_7.setObjectName(u"CB_plot_7")

        self.gridLayout_4.addWidget(self.CB_plot_7, 1, 2, 1, 1)

        self.CB_plot_8 = QCheckBox(self.group_live_control)
        self.CB_plot_8.setObjectName(u"CB_plot_8")

        self.gridLayout_4.addWidget(self.CB_plot_8, 1, 3, 1, 1)


        self.verticalLayout_13.addLayout(self.gridLayout_4)


        self.verticalLayout_15.addWidget(self.group_live_control)

        self.group_acquire_control = QGroupBox(self.groupBox_10)
        self.group_acquire_control.setObjectName(u"group_acquire_control")
        self.group_acquire_control.setFlat(True)
        self.verticalLayout_14 = QVBoxLayout(self.group_acquire_control)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.PB_acquire_start = QPushButton(self.group_acquire_control)
        self.PB_acquire_start.setObjectName(u"PB_acquire_start")

        self.verticalLayout_14.addWidget(self.PB_acquire_start)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_8 = QLabel(self.group_acquire_control)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_9.addWidget(self.label_8)

        self.LE_num_dft_acquire = QLineEdit(self.group_acquire_control)
        self.LE_num_dft_acquire.setObjectName(u"LE_num_dft_acquire")

        self.horizontalLayout_9.addWidget(self.LE_num_dft_acquire)


        self.verticalLayout_14.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_9 = QLabel(self.group_acquire_control)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_10.addWidget(self.label_9)

        self.LE_acquire_time = QLineEdit(self.group_acquire_control)
        self.LE_acquire_time.setObjectName(u"LE_acquire_time")

        self.horizontalLayout_10.addWidget(self.LE_acquire_time)

        self.label_elapsed_time = QLabel(self.group_acquire_control)
        self.label_elapsed_time.setObjectName(u"label_elapsed_time")

        self.horizontalLayout_10.addWidget(self.label_elapsed_time)


        self.verticalLayout_14.addLayout(self.horizontalLayout_10)

        self.Progress_Acquistion = QProgressBar(self.group_acquire_control)
        self.Progress_Acquistion.setObjectName(u"Progress_Acquistion")
        self.Progress_Acquistion.setValue(0)

        self.verticalLayout_14.addWidget(self.Progress_Acquistion)


        self.verticalLayout_15.addWidget(self.group_acquire_control)


        self.horizontalLayout_5.addWidget(self.groupBox_10)

        self.group_spectrum = QGroupBox(self.group_viewer)
        self.group_spectrum.setObjectName(u"group_spectrum")
        self.group_spectrum.setFlat(True)
        self.layout_spectrum = QVBoxLayout(self.group_spectrum)
        self.layout_spectrum.setObjectName(u"layout_spectrum")
        self.layout_spectrum.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_5.addWidget(self.group_spectrum)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 5)

        self.verticalLayout_12.addWidget(self.group_viewer)

        self.group_save_control = QGroupBox(self.group_viviewer)
        self.group_save_control.setObjectName(u"group_save_control")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.group_save_control.sizePolicy().hasHeightForWidth())
        self.group_save_control.setSizePolicy(sizePolicy)
        self.group_save_control.setMaximumSize(QSize(16777215, 50))
        self.group_save_control.setFlat(False)
        self.horizontalLayout_4 = QHBoxLayout(self.group_save_control)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(6, 0, 6, 0)
        self.label_3 = QLabel(self.group_save_control)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.LE_save_path = QLineEdit(self.group_save_control)
        self.LE_save_path.setObjectName(u"LE_save_path")

        self.horizontalLayout_4.addWidget(self.LE_save_path)

        self.PB_browse = QPushButton(self.group_save_control)
        self.PB_browse.setObjectName(u"PB_browse")

        self.horizontalLayout_4.addWidget(self.PB_browse)

        self.PB_open = QPushButton(self.group_save_control)
        self.PB_open.setObjectName(u"PB_open")

        self.horizontalLayout_4.addWidget(self.PB_open)

        self.save_status = QLabel(self.group_save_control)
        self.save_status.setObjectName(u"save_status")

        self.horizontalLayout_4.addWidget(self.save_status)


        self.verticalLayout_12.addWidget(self.group_save_control)

        self.group_tabs = QGroupBox(self.group_viviewer)
        self.group_tabs.setObjectName(u"group_tabs")
        self.group_tabs.setFlat(False)
        self.horizontalLayout_8 = QHBoxLayout(self.group_tabs)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.tabs_spectrogram = QTabWidget(self.group_tabs)
        self.tabs_spectrogram.setObjectName(u"tabs_spectrogram")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tabs_spectrogram.sizePolicy().hasHeightForWidth())
        self.tabs_spectrogram.setSizePolicy(sizePolicy1)
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 236, 236, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(99, 255, 255, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(49, 245, 245, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(0, 118, 118, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush4)
        brush5 = QBrush(QColor(0, 157, 157, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush6 = QBrush(QColor(255, 255, 255, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush6)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush6)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush7 = QBrush(QColor(127, 245, 245, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush7)
        brush8 = QBrush(QColor(255, 255, 220, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush8)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush)
        self.tabs_spectrogram.setPalette(palette)
        self.tabs_spectrogram.setAutoFillBackground(False)

        self.horizontalLayout_8.addWidget(self.tabs_spectrogram)


        self.verticalLayout_12.addWidget(self.group_tabs)

        self.verticalLayout_12.setStretch(0, 4)
        self.verticalLayout_12.setStretch(1, 1)
        self.verticalLayout_12.setStretch(2, 12)

        self.horizontalLayout.addWidget(self.group_viviewer)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 4)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabs_spectrogram.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.group_left.setTitle("")
        self.group_device.setTitle("")
        self.PB_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.PB_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.group_device_setting.setTitle("")
        self.group_allgain.setTitle("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"All Gains: ", None))
        self.group_sampling.setTitle("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Sampling (Hz): ", None))
        self.group_channel_8.setTitle(QCoreApplication.translate("MainWindow", u"Ch 8", None))
        self.TB_gains_label_8.setText(QCoreApplication.translate("MainWindow", u"Ch 8", None))
        self.group_channel_6.setTitle(QCoreApplication.translate("MainWindow", u"Ch 6", None))
        self.TB_gains_label_6.setText(QCoreApplication.translate("MainWindow", u"Ch 6", None))
        self.group_channel_7.setTitle(QCoreApplication.translate("MainWindow", u"Ch 7", None))
        self.TB_gains_label_7.setText(QCoreApplication.translate("MainWindow", u"Ch 7", None))
        self.group_channel_3.setTitle(QCoreApplication.translate("MainWindow", u"Ch 3", None))
        self.TB_gains_label_3.setText(QCoreApplication.translate("MainWindow", u"Ch 3", None))
        self.group_channel_4.setTitle(QCoreApplication.translate("MainWindow", u"Ch 4", None))
        self.TB_gains_label_4.setText(QCoreApplication.translate("MainWindow", u"Ch 4", None))
        self.group_channel_2.setTitle(QCoreApplication.translate("MainWindow", u"Ch 2", None))
        self.TB_gains_label_2.setText(QCoreApplication.translate("MainWindow", u"Ch 2", None))
        self.group_channel_1.setTitle(QCoreApplication.translate("MainWindow", u"Ch 1", None))
        self.TB_gains_label_1.setText(QCoreApplication.translate("MainWindow", u"Ch 1", None))
        self.group_channel_5.setTitle(QCoreApplication.translate("MainWindow", u"Ch 5", None))
        self.TB_gains_label_5.setText(QCoreApplication.translate("MainWindow", u"Ch 5", None))
        self.group_cmd.setTitle("")
        self.PB_closeCMD.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.PB_send.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.PB_clear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.group_logo.setTitle("")
        self.group_viviewer.setTitle("")
        self.group_viewer.setTitle("")
        self.groupBox_10.setTitle("")
        self.group_live_control.setTitle("")
        self.PB_live_start.setText(QCoreApplication.translate("MainWindow", u"Live: Start", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"# Live Sample", None))
        self.LE_num_live_sample.setText(QCoreApplication.translate("MainWindow", u"512", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"# DFT", None))
        self.LE_num_dft_live.setText(QCoreApplication.translate("MainWindow", u"128", None))
        self.CheckBox_average.setText(QCoreApplication.translate("MainWindow", u"Show Average", None))
        self.CB_plot_4.setText("")
        self.CB_plot_3.setText("")
        self.CB_plot_2.setText("")
        self.CB_plot_1.setText("")
        self.CB_plot_5.setText("")
        self.CB_plot_6.setText("")
        self.CB_plot_7.setText("")
        self.CB_plot_8.setText("")
        self.group_acquire_control.setTitle("")
        self.PB_acquire_start.setText(QCoreApplication.translate("MainWindow", u"Acquire: Start", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"# DFT", None))
        self.LE_num_dft_acquire.setText(QCoreApplication.translate("MainWindow", u"1024", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"times (s)", None))
        self.LE_acquire_time.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.label_elapsed_time.setText(QCoreApplication.translate("MainWindow", u"0 s", None))
        self.group_spectrum.setTitle("")
        self.group_save_control.setTitle("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Save Path:", None))
        self.PB_browse.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.PB_open.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.save_status.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.group_tabs.setTitle("")
    # retranslateUi

