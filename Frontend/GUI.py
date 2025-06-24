from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QProgressBar)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from dotenv import dotenv_values
import sys
import os
import queue
import threading

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "JARVIS")
Username = env_vars.get("Username", "User")

# Directory paths
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

class AuthenticationScreen(QWidget):
    def __init__(self, parent=None, on_success=None):
        super().__init__(parent)
        self.on_success = on_success
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel("JARVIS AUTHENTICATION")
        title.setStyleSheet("""
            color: #00FFFF;
            font-size: 36px;
            font-weight: bold;
            font-family: 'Courier New';
            margin-bottom: 30px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("Initializing face recognition...")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-family: 'Courier New';
            margin-bottom: 20px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00FFFF;
                border-radius: 5px;
                text-align: center;
                background-color: black;
                color: white;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #00FFFF;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Instructions
        instructions = QLabel("Look directly at the camera for authentication")
        instructions.setStyleSheet("""
            color: #CCCCCC;
            font-size: 16px;
            font-family: 'Courier New';
            margin-top: 20px;
        """)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        # Skip button (for testing)
        skip_button = QPushButton("Skip Authentication (Testing)")
        skip_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: 2px solid #666666;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                margin-top: 30px;
            }
            QPushButton:hover {
                background-color: #555555;
                border-color: #888888;
            }
        """)
        skip_button.clicked.connect(self.skip_authentication)
        layout.addWidget(skip_button)
        
        self.setLayout(layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        
        # Start authentication timer
        self.auth_timer = QTimer()
        self.auth_timer.timeout.connect(self.update_progress)
        self.auth_timer.start(100)
        self.progress_value = 0
        
    def update_progress(self):
        self.progress_value += 2
        self.progress_bar.setValue(self.progress_value)
        
        if self.progress_value >= 100:
            self.auth_timer.stop()
            self.authenticate()
    
    def authenticate(self):
        # Simulate authentication process
        self.status_label.setText("Authentication successful!")
        QTimer.singleShot(1000, self.on_success)
    
    def skip_authentication(self):
        self.on_success()

class ChatSection(QWidget):
    def __init__(self, gui_update_queue, mic_status_queue):
        super(ChatSection, self).__init__()
        self.gui_update_queue = gui_update_queue
        self.mic_status_queue = mic_status_queue
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 40, 100)
        layout.setSpacing(10)

        # Chat display
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.8);
                color: #00FFFF;
                font-family: 'Courier New';
                font-size: 14px;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_text_edit)

        # JARVIS animation
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(rf"{GraphicsDirPath}\Jarvis.gif")
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("""
            color: #00FFFF;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Courier New';
            margin-right: 195px;
            border: none;
            margin-top: -30px;
        """)
        self.status_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.status_label)

        self.setStyleSheet("background-color: black;")
        
        # Timer for updating GUI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_from_queue)
        self.timer.start(50)  # Update every 50ms for responsiveness

    def update_from_queue(self):
        """Update GUI from queue messages"""
        try:
            while not self.gui_update_queue.empty():
                message_type, content = self.gui_update_queue.get_nowait()
                if message_type == 'chat':
                    self.addMessage(content, '#00FFFF')
                elif message_type == 'status':
                    self.status_label.setText(content)
        except queue.Empty:
            pass

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
        # Auto-scroll to bottom
        scrollbar = self.chat_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class InitialScreen(QWidget):
    def __init__(self, gui_update_queue, mic_status_queue, parent=None):
        super().__init__(parent)
        self.gui_update_queue = gui_update_queue
        self.mic_status_queue = mic_status_queue
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # JARVIS animation
        gif_label = QLabel()
        movie = QMovie(rf'{GraphicsDirPath}\Jarvis.gif')
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Microphone button
        self.icon_label = QLabel()
        pixmap = QPixmap(rf'{GraphicsDirPath}\Mic_off.png')
        new_pixmap = pixmap.scaled(80, 80)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                border: 3px solid #00FFFF;
                border-radius: 75px;
                background-color: rgba(0, 255, 255, 0.1);
            }
            QLabel:hover {
                background-color: rgba(0, 255, 255, 0.2);
                border-color: #FFFFFF;
            }
        """)
        self.toggled = False
        self.icon_label.mousePressEvent = self.toggle_icon

        # Status label
        self.status_label = QLabel("Ready to assist...")
        self.status_label.setStyleSheet("""
            color: #00FFFF;
            font-size: 20px;
            font-weight: bold;
            font-family: 'Courier New';
            margin-bottom: 20px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        # Timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(100)

    def update_status(self):
        """Update status from queue"""
        try:
            while not self.gui_update_queue.empty():
                message_type, content = self.gui_update_queue.get_nowait()
                if message_type == 'status':
                    self.status_label.setText(content)
        except queue.Empty:
            pass

    def load_icon(self, path, width=80, height=80):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(rf'{GraphicsDirPath}\Mic_off.png')
            self.mic_status_queue.put(False)
        else:
            self.load_icon(rf'{GraphicsDirPath}\Mic_on.png')
            self.mic_status_queue.put(True)
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, gui_update_queue, mic_status_queue, parent=None):
        super().__init__(parent)
        self.gui_update_queue = gui_update_queue
        self.mic_status_queue = mic_status_queue
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout()
        chat_section = ChatSection(self.gui_update_queue, self.mic_status_queue)
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        # JARVIS title
        title_label = QLabel("J.A.R.V.I.S")
        title_label.setStyleSheet("""
            color: #00FFFF;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Courier New';
            margin-left: 20px;
        """)
        layout.addWidget(title_label)
        layout.addStretch()

        # Navigation buttons
        home_button = QPushButton("HOME")
        home_button.setStyleSheet(self.get_button_style())
        home_button.clicked.connect(self.showInitialScreen)

        message_button = QPushButton("CHAT")
        message_button.setStyleSheet(self.get_button_style())
        message_button.clicked.connect(self.showMessageScreen)

        # Window controls
        minimize_button = QPushButton("−")
        minimize_button.setStyleSheet(self.get_control_button_style())
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton("□")
        self.maximize_button.setStyleSheet(self.get_control_button_style())
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton("×")
        close_button.setStyleSheet(self.get_control_button_style("#FF0000"))
        close_button.clicked.connect(self.closeWindow)

        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.9); border-bottom: 2px solid #00FFFF;")

    def get_button_style(self):
        return """
            QPushButton {
                background-color: transparent;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Courier New';
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 255, 0.2);
                color: white;
            }
            QPushButton:pressed {
                background-color: rgba(0, 255, 255, 0.4);
            }
        """

    def get_control_button_style(self, color="#00FFFF"):
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {color};
                border: 2px solid {color};
                padding: 8px 12px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                margin: 5px;
                min-width: 30px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
            }}
        """

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setText("□")
        else:
            self.parent().showMaximized()
            self.maximize_button.setText("❐")

    def closeWindow(self):
        self.parent().close()

    def showMessageScreen(self):
        self.stacked_widget.setCurrentIndex(2)

    def showInitialScreen(self):
        self.stacked_widget.setCurrentIndex(1)

class MainWindow(QMainWindow):
    def __init__(self, gui_update_queue, mic_status_queue):
        super(MainWindow, self).__init__()
        self.gui_update_queue = gui_update_queue
        self.mic_status_queue = mic_status_queue
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        self.stacked_widget = QStackedWidget(self)
        
        # Authentication screen
        auth_screen = AuthenticationScreen(on_success=self.show_main_interface)
        self.stacked_widget.addWidget(auth_screen)
        
        # Main screens
        initial_screen = InitialScreen(self.gui_update_queue, self.mic_status_queue)
        message_screen = MessageScreen(self.gui_update_queue, self.mic_status_queue)
        
        self.stacked_widget.addWidget(initial_screen)
        self.stacked_widget.addWidget(message_screen)
        
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        
        # Top bar
        top_bar = CustomTopBar(self, self.stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(self.stacked_widget)
        
        # Start with authentication
        self.stacked_widget.setCurrentIndex(0)
    
    def show_main_interface(self):
        """Show main interface after authentication"""
        self.stacked_widget.setCurrentIndex(1)

def GraphicalUserInterface(gui_update_queue, mic_status_queue):
    """Main GUI function"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("JARVIS AI Assistant")
    app.setApplicationVersion("2.0")
    
    window = MainWindow(gui_update_queue, mic_status_queue)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Test GUI
    gui_queue = queue.Queue()
    mic_queue = queue.Queue()
    GraphicalUserInterface(gui_queue, mic_queue)