from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
old_chat_message = ""
# Directory paths
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words  = new_query.split()
    question_words = ['how','what','who','where','when','why','which','whom','can you',"what's", "where's","how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
        file.write(Command)
    

def GetMicrophoneStatus():
    
    with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
        Status = file.read().strip()
    return Status


def SetAsssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data','w',encoding='utf-8') as file:
        file.write(Status)


def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
        Status = file.read()
    return Status
    

    
# Define placeholders for the missing functions
def MicButtonInitiated():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    path = rf'{GraphicsDirPath}\{Filename}'
    return path


def TempDirectoryPath(Filename):
    path = rf'{TempDirPath}\{Filename}'
    return path

def ShowTextToScreen(Text):
    with open (rf'{TempDirPath}\Responses.data','w', encoding='utf-8') as file:
        file.write(Text)

    
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        self.movie = QMovie(rf"{GraphicsDirPath}\Jarvis.gif")
        max_gif_size_W = 480
        max_gif_size_H = 270
        self.movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(250)

        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            if messages and messages != old_chat_message:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            self.label.setText(messages)
        except FileNotFoundError:
            pass

    def load_icon(self, path, width=60, height=60):
        if hasattr(self, 'icon_label'):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if getattr(self, 'toggled', False):
            self.load_icon(rf'{GraphicsDirPath}\Mic_on.png', 60, 60)
            MicButtonInitiated()
        else:
            self.load_icon(rf'{GraphicsDirPath}\Mic_off.png', 60, 60)
            MicButtonClosed()
        self.toggled = not getattr(self, 'toggled', False)

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)



class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 20, 0, 30)
        content_layout.setSpacing(15)

        gif_label = QLabel()
        self.movie = QMovie(GraphicsDirPath + r'\Jarvis.gif')
        gif_label.setMovie(self.movie)
        gif_w = min(int(screen_width * 0.55), 640)
        gif_h = int(gif_w / 16 * 9)
        self.movie.setScaledSize(QSize(gif_w, gif_h))
        gif_label.setAlignment(Qt.AlignCenter)
        self.movie.start()

        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirPath + r'\Mic_off.png')
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = False
        SetMicrophoneStatus("False")
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom: 0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        self.setLayout(content_layout)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(250)

    def SpeechRecogText(self):
        try:
            with open(TempDirPath + r'\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
            with open(TempDirPath + r'\Mic.data', 'r', encoding='utf-8') as file:
                mic_state = file.read().strip().lower()
                if mic_state == "false" and self.toggled:
                    self.toggled = False
                    self.load_icon(GraphicsDirPath + r'\Mic_off.png', 60, 60)
        except Exception:
            pass

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            # Turn OFF
            self.load_icon(GraphicsDirPath + r'\Mic_off.png', 60, 60)
            SetMicrophoneStatus("False")
            self.toggled = False
        else:
            # Turn ON
            self.load_icon(GraphicsDirPath + r'\Mic_on.png', 60, 60)
            SetMicrophoneStatus("True")
            self.toggled = True


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.current_screen = None
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: #141414;")
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)

        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirPath + r'\Home.png')
        home_button.setIcon(home_icon)
        home_button.setText("   Home")
        home_button.setStyleSheet("height:36px; background-color:#222; color: white; border: 1px solid #444; border-radius: 4px; padding: 0 15px; font-weight: bold;")
        home_button.clicked.connect(self.showInitialScreen)

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirPath + r'\Message.png')
        message_button.setIcon(message_icon)
        message_button.setText("   Message")
        message_button.setStyleSheet("height:36px; background-color:#222; color: white; border: 1px solid #444; border-radius: 4px; padding: 0 15px; font-weight: bold;")
        message_button.clicked.connect(self.showMessageScreen)

        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch()
        layout.setContentsMargins(15, 7, 15, 7)

    def showMessageScreen(self):
        self.stacked_widget.setCurrentIndex(1)

    def showInitialScreen(self):
        self.stacked_widget.setCurrentIndex(0)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS - AI Assistant")
        self.setWindowIcon(QIcon(GraphicsDirPath + r'\Home.png'))
        self.setStyleSheet("background-color: black;")
        self.initUI()

    def initUI(self):
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QApplication.desktop().availableGeometry()
        
        self.stacked_widget = QStackedWidget(self)
        self.initial_screen = InitialScreen()
        self.message_screen = MessageScreen()
        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.message_screen)

        win_w = min(1050, avail.width() - 40)
        win_h = min(680, avail.height() - 40)
        self.resize(win_w, win_h)
        self.move((avail.width() - win_w) // 2, (avail.height() - win_h) // 2)

        central_container = QWidget(self)
        central_layout = QVBoxLayout(central_container)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        top_bar = CustomTopBar(self, self.stacked_widget)
        central_layout.addWidget(top_bar)
        central_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(central_container)

def AttachToDefaultDesktop():
    """Attaches process and thread to the physical interactive desktop (WinSta0\\Default)."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwinsta = user32.OpenWindowStationW('WinSta0', False, 0x037F)
        if hwinsta:
            user32.SetProcessWindowStation(hwinsta)
            hdesk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

def GraphicalUserInterface():
    AttachToDefaultDesktop()

    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('jarvis.assistant.gui.v1')
    except Exception:
        pass

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowFlags(Qt.Window)
    window.show()
    window.raise_()
    window.activateWindow()

    try:
        import ctypes
        hwnd = int(window.winId())
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception:
        pass

    print("[GUI Ready] JARVIS Assistant window is now open on your screen.")
    sys.exit(app.exec_())

# Run the application
if __name__ == "__main__":
    GraphicalUserInterface()