from PySide6 import QtWidgets  # Should work with PyQt5 / PySide2 / PySide6 as well
import pyqtgraph as pg

# Always start by initializing Qt (only once per application)
app = QtWidgets.QApplication([])

# Define a top-level widget to hold everything
w = QtWidgets.QWidget()
w.setWindowTitle('PyQtGraph example')

# Create some widgets to be placed inside
btn = QtWidgets.QPushButton('press me')
text = QtWidgets.QLineEdit('enter text')
listWidget = QtWidgets.QListWidget()
plot = pg.PlotWidget()

# Create a grid layout to manage the widgets size and position
layout = QtWidgets.QGridLayout()
w.setLayout(layout)

# Add widgets to the layout in their proper positions
layout.addWidget(btn, 0, 0)  # button goes in upper-left
layout.addWidget(text, 1, 0)  # text edit goes in middle-left
layout.addWidget(listWidget, 2, 0)  # list widget goes in bottom-left
layout.addWidget(plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows
# Display the widget as a new window
w.show()

# Start the Qt event loop
app.exec()  # or app.exec_() for PyQt5 / PySide2