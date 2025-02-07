from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt,Signal

class device_console(QTextEdit):
    signal_send_command = Signal( str )
    def __init__(self, name = ""):
        super().__init__()
        self.cursor = self.textCursor()

        if name == "":
            name = "device"
        init_msg = f"Connect to a {name}: "

        self.setWindowTitle(name)

        self.resize( 500,350 )
        self.setEnabled(False)

        self.append(init_msg)
        # Initialize with '> '
        self.append("> ")

    def appear( self ):
        self.close()
        self.show()

    def keyPressEvent(self, event):
        if len(repr(event.text())) == 3 :  # Normal Text
            # Block edits to previous lines
            self.cursor.movePosition(QTextCursor.End)
            self.setTextCursor(self.cursor)
            super().keyPressEvent(event)

        elif event.key() == Qt.Key_Return:  # Enter key
            # Get the last line + EOL from previous line
            last_line = self.extract_lastline()

            # Process the last line (e.g., send to terminal)
            cmd = last_line[3:] # Remove "> "
            self.signal_send_command.emit( cmd )   
            # Add it back with new line
            self.append(cmd+"\n")   

            # Add a new editable line at the end
            self.append("> ")
            self.cursor.movePosition(QTextCursor.End)  
            self.setTextCursor(self.cursor)

        else: # All other keys
            super().keyPressEvent(event)


    def extract_lastline(self,n=1):
        self.cursor.movePosition(QTextCursor.End)
        self.cursor.movePosition(QTextCursor.StartOfLine)
        self.cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor,n)
        self.cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)

        last_line = self.cursor.selectedText()      
        self.cursor.removeSelectedText()   
        return last_line


    def msg_received(self, msg):
        last_line = self.extract_lastline(2)
        self.append( msg + last_line)
        self.cursor.movePosition(QTextCursor.End)

