#! /bin/bash

pyside6-uic -o UI_makers/vivi_makeUI_main.py assets/ui_files/vivi_mainWindow.ui
pyside6-uic -o UI_makers/vivi_makeUI_adcSetting.py assets/ui_files/vivi_adcSetting.ui
pyside6-uic -o UI_makers/vivi_makeUI_adcFullSetting.py assets/ui_files/vivi_adcFullSetting.ui
# pyside6-uic -o UI_makers/mili_makeUI_sensor.py assets/ui_files/mili_sensor.ui
# pyside6-uic -o UI_makers/mili_makeUI_output.py assets/ui_files/mili_output.ui
# # pyside6-uic -o UI_makers/mili_makeUI_about.py assets/ui_files/mili-about.ui
# pyside6-uic -o UI_makers/mili_makeUI_pid.py assets/ui_files/mili_pid.ui
# pyside6-uic -o UI_makers/mili_makeUI_save.py assets/ui_files/mili_save.ui
# pyside6-uic -o UI_makers/mili_makeUI_inputSetting.py assets/ui_files/mili_inputSetting.ui
# pyside6-uic -o UI_makers/mili_makeUI_mainPlot.py assets/ui_files/mili_mainPlot.ui
# pyside6-uic -o UI_makers/mili_makeUI_miniPlot.py assets/ui_files/mili_miniPlot.ui
pyside6-uic -o UI_makers/vivi_makeUI_deviceDialog.py assets/ui_files/vivi_deviceDialog.ui
pyside6-uic -o UI_makers/vivi_makeUI_deviceManager.py assets/ui_files/vivi_deviceManager.ui
# pyside6-uic -o UI_makers/mili_makeUI_flow.py assets/ui_files/mili_flow.ui
# pyside6-uic -o UI_makers/mili_makeUI_console.py assets/ui_files/mili_console.ui