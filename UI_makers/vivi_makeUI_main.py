# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vivi_mainWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 718)
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
        self.group_vivi_control = QStackedWidget(self.group_left)
        self.group_vivi_control.setObjectName(u"group_vivi_control")
        self.group_vivi_off = QWidget()
        self.group_vivi_off.setObjectName(u"group_vivi_off")
        self.group_vivi_control.addWidget(self.group_vivi_off)
        self.group_vivi_on = QWidget()
        self.group_vivi_on.setObjectName(u"group_vivi_on")
        self.verticalLayout = QVBoxLayout(self.group_vivi_on)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.group_sampling = QGroupBox(self.group_vivi_on)
        self.group_sampling.setObjectName(u"group_sampling")
        self.group_sampling.setFlat(True)
        self.horizontalLayout_15 = QHBoxLayout(self.group_sampling)
        self.horizontalLayout_15.setSpacing(0)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.group_allgain = QGroupBox(self.group_sampling)
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
        self.CB_allGains.addItem("")
        self.CB_allGains.addItem("")
        self.CB_allGains.addItem("")
        self.CB_allGains.addItem("")
        self.CB_allGains.addItem("")
        self.CB_allGains.addItem("")
        self.CB_allGains.addItem("")
        self.CB_allGains.setObjectName(u"CB_allGains")
        self.CB_allGains.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_14.addWidget(self.CB_allGains)


        self.horizontalLayout_15.addWidget(self.group_allgain)

        self.label_2 = QLabel(self.group_sampling)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_15.addWidget(self.label_2)

        self.LE_sampling = QLineEdit(self.group_sampling)
        self.LE_sampling.setObjectName(u"LE_sampling")
        self.LE_sampling.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_15.addWidget(self.LE_sampling)


        self.verticalLayout.addWidget(self.group_sampling)

        self.layout_adc = QGridLayout()
        self.layout_adc.setObjectName(u"layout_adc")
        self.layout_adc.setHorizontalSpacing(0)

        self.verticalLayout.addLayout(self.layout_adc)

        self.verticalLayout.setStretch(1, 1)
        self.group_vivi_control.addWidget(self.group_vivi_on)

        self.layout_left.addWidget(self.group_vivi_control)

        self.group_logo_enable = QGroupBox(self.group_left)
        self.group_logo_enable.setObjectName(u"group_logo_enable")
        self.group_logo_enable.setFlat(True)

        self.layout_left.addWidget(self.group_logo_enable)

        self.layout_left.setStretch(0, 1)
        self.layout_left.setStretch(1, 1)

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
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer)

        self.group_live_control = QGroupBox(self.groupBox_10)
        self.group_live_control.setObjectName(u"group_live_control")
        self.group_live_control.setFlat(True)
        self.verticalLayout_13 = QVBoxLayout(self.group_live_control)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 12, 0, 0)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 0, -1, -1)
        self.label_8 = QLabel(self.group_live_control)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_7.addWidget(self.label_8)

        self.LE_num_dft = QLineEdit(self.group_live_control)
        self.LE_num_dft.setObjectName(u"LE_num_dft")

        self.horizontalLayout_7.addWidget(self.LE_num_dft)


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
        self.PB_live_start = QPushButton(self.group_acquire_control)
        self.PB_live_start.setObjectName(u"PB_live_start")

        self.verticalLayout_14.addWidget(self.PB_live_start)

        self.PB_acquire_start = QPushButton(self.group_acquire_control)
        self.PB_acquire_start.setObjectName(u"PB_acquire_start")

        self.verticalLayout_14.addWidget(self.PB_acquire_start)

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

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 5)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.group_vivi_control.setCurrentIndex(1)
        self.tabs_spectrogram.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.group_left.setTitle("")
        self.group_sampling.setTitle("")
        self.group_allgain.setTitle("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"All Gains: ", None))
        self.CB_allGains.setItemText(0, QCoreApplication.translate("MainWindow", u"128", None))
        self.CB_allGains.setItemText(1, QCoreApplication.translate("MainWindow", u"64", None))
        self.CB_allGains.setItemText(2, QCoreApplication.translate("MainWindow", u"32", None))
        self.CB_allGains.setItemText(3, QCoreApplication.translate("MainWindow", u"16", None))
        self.CB_allGains.setItemText(4, QCoreApplication.translate("MainWindow", u"8", None))
        self.CB_allGains.setItemText(5, QCoreApplication.translate("MainWindow", u"1", None))
        self.CB_allGains.setItemText(6, "")

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Sampling (Hz): ", None))
        self.LE_sampling.setText(QCoreApplication.translate("MainWindow", u"400", None))
        self.group_logo_enable.setTitle("")
        self.group_viviewer.setTitle("")
        self.group_viewer.setTitle("")
        self.groupBox_10.setTitle("")
        self.group_live_control.setTitle("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"# DFT", None))
        self.LE_num_dft.setText(QCoreApplication.translate("MainWindow", u"1024", None))
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
        self.PB_live_start.setText(QCoreApplication.translate("MainWindow", u"Live: Start", None))
        self.PB_acquire_start.setText(QCoreApplication.translate("MainWindow", u"Acquire: Start", None))
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

