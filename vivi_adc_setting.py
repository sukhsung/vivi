from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from UI_makers.vivi_makeUI_adcSetting import Ui_adc_setting
from UI_makers.vivi_makeUI_adcFullSetting import Ui_adc_full_setting

class adc_full_setting( Ui_adc_full_setting):
    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        self.widget.setObjectName("Test")
        self.setupUi(self.widget)
        

class adc_setting( Ui_adc_setting ):
    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        self.widget.setObjectName("Test")
        self.setupUi(self.widget)
        