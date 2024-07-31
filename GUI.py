from PyQt5.QtWidgets import QApplication, QLabel, QFrame, QMainWindow, QGraphicsDropShadowEffect, QVBoxLayout, QWidget, QLabel, QLineEdit, QTextEdit, QPlainTextEdit, QProgressBar, QSlider, QStyleFactory, QSplitter, QSizePolicy, QSpacerItem, QPushButton, QTextBrowser, QScrollArea, QStatusBar, QDockWidget, QToolBar, QToolButton, QDesktopWidget
from PyQt5.QtCore import QTimer, Q_ARG, QRunnable, QDateTime, QEventLoop, QAbstractEventDispatcher, Qt, QMetaObject, QThreadPool, QObject, QPropertyAnimation
from PyQt5.QtGui import QTextCursor, QIcon, QFont
from PIL import Image, ImageQt
from Anthony_AI import anthony_ai
from tkinter import filedialog
from tkinter import Tk
import numpy as np
import asyncio
import easyocr
import fitz
import sys

app = QApplication(sys.argv) 

dispatcher = QAbstractEventDispatcher.instance()

class CustomEventLoop(QEventLoop, QObject):
    def create_asyncio_loop(self):
        return asyncio.new_event_loop()

def set_custom_event_loop_policy():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

set_custom_event_loop_policy()

class RunCoroutine(QRunnable):
    def __init__(self, coroutine):
        super().__init__()
        self.coroutine = coroutine

    def run(self):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.coroutine)
        finally:
            loop.close()
            
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Futuristic Assistant")
        screen_geometry = QDesktopWidget().availableGeometry()  # Get the screen geometry
        self.setGeometry(0, 0, screen_geometry.width(), screen_geometry.height())  # Set the window size to full screen
        self.setWindowIcon(QIcon('icon.png'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.menu_button = QPushButton("")  # Create the menu button
        self.menu_button.setIcon(QIcon("menu_icon.png"))
        self.menu_button.setFlat(True)
        self.menu_button.clicked.connect(self.toggle_menu)
        self.menu_button.setFixedSize(40, 40)  # Set the button size
        self.menu_button.setStyleSheet("QPushButton {background-color: #3a3b3e; border: none; border-radius: 10px; padding: 10px}")
        self.menu_button.move(10, 10)  # Move the button to the top-left corner

        self.left_menu = QDockWidget("Menu", self)
        self.left_menu.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_menu)

        self.menu_widget = QWidget()
        self.left_menu.setWidget(self.menu_widget)

        self.menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(self.menu_layout)

        self.menu_layout.setContentsMargins(10, 10, 10, 10)  # Add some margins
        self.menu_layout.setSpacing(10)  # Add some spacing between items

        self.settings_button = QPushButton("Settings")
        self.settings_button.setIcon(QIcon("settings_icon.png"))
        self.settings_button.setFlat(True)
        self.menu_layout.addWidget(self.settings_button)

        self.theme_button = QPushButton("Switch Theme")
        self.theme_button.setIcon(QIcon("theme_icon.png"))
        self.theme_button.setFlat(True)
        self.theme_button.clicked.connect(self.switch_theme)
        self.menu_layout.addWidget(self.theme_button)

        self.voice_assistant_button = QPushButton("Voice Assistant")
        self.voice_assistant_button.setIcon(QIcon("voice_assistant_icon.png"))
        self.voice_assistant_button.setFlat(True)
        self.menu_layout.addWidget(self.voice_assistant_button)

        self.about_button = QPushButton("About")
        self.about_button.setIcon(QIcon("about_icon.png"))
        self.about_button.setFlat(True)
        self.menu_layout.addWidget(self.about_button)

        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.menu_layout.addWidget(separator)

        # Add a label
        label = QLabel("Anthony AI")
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        self.menu_layout.addWidget(label)

        # Add a spacer
        spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.menu_layout.addItem(spacer)

        # Set menu style
        self.menu_widget.setStyleSheet("""
            QWidget {
                background-color: #2f2f2f;
                border: none;
            }
            QPushButton {
                background-color: #3a3b3e;
                color: #fff;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #444547;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #fff;
            }
            QFrame {
                background-color: #444547;
                height: 2px;
                margin: 10px 0;
            }
        """)

        self.menu_button = QPushButton("")
        self.menu_button.setIcon(QIcon("menu_icon.png"))
        self.menu_button.setFlat(True)
        self.menu_button.clicked.connect(self.toggle_menu)
        self.menu_layout.addWidget(self.menu_button)

        self.chat_area = QWidget()
        self.main_layout.addWidget(self.chat_area)

        self.chat_layout = QVBoxLayout()
        self.chat_area.setLayout(self.chat_layout)

        self.chat_text_edit = QTextEdit()
        self.chat_layout.addWidget(self.chat_text_edit)

        self.input_area = QWidget()
        self.main_layout.addWidget(self.input_area)

        self.input_layout = QVBoxLayout()
        self.input_area.setLayout(self.input_layout)

        self.line_edit = QLineEdit()
        self.input_layout.addWidget(self.line_edit)

        self.send_button = QPushButton("Envoyer")
        self.input_layout.addWidget(self.send_button)

        self.voice_output_button = QToolButton()
        self.voice_output_button.setIcon(QIcon("voice_output_icon.png"))
        self.voice_output_button.setCheckable(True)
        self.input_layout.addWidget(self.voice_output_button)

        self.microphone_button = QToolButton()
        self.microphone_button.setIcon(QIcon("microphone_icon.png"))
        self.microphone_button.setCheckable(True)
        self.input_layout.addWidget(self.microphone_button)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.send_button.clicked.connect(self.on_button_clicked)

        self.theme = "dark"  # Set the default theme to dark
        self.switch_theme()

    def toggle_menu(self):
        if self.menu_widget.maximumWidth() == 0:
            self.menu_widget.setMaximumWidth(200)
        else:
            self.menu_widget.setMaximumWidth(50)

    def process_pdf(self):
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])

        # Create a Tkinter instance to use the file dialog
        root = Tk()
        root.withdraw()  # Hide the Tkinter window

        # Open file dialog to select the PDF file
        file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])

        # Open the selected PDF file
        doc = fitz.open(file_path)

        # Loop through each page and extract text
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pixmap = page.get_pixmap()
            img_data = pixmap.tobytes("png")  # Convert to PNG bytes
            result = reader.readtext(img_data)
            text = ' '.join([item[1] for item in result])  # Récupère uniquement le texte détecté
            print(text)

    def switch_theme(self):
        if self.theme == "light":
            self.theme = "dark"
            self.setStyleSheet("""
                QMainWindow {background: '#f0f0f0';}
                QTextEdit {background: '#fff'; color: #000; border: none;}
                QPushButton {background-color: #4CAF50; color: #fff; border-radius: 10px; padding: 10px}
                QPushButton:hover {background-color: #3e8e41}
                QToolButton {background-color: #3a3b3e; border: none; border-radius: 10px; padding: 10px}
                QToolButton:hover {background-color: #444547}
                QLabel {font-size: 16px; font-weight: bold; color: #000;}
            """)
        else:
            self.theme = "light"
            self.setStyleSheet("""
                QMainWindow {background: '#2f2f2f';}
                QTextEdit {background: '#333'; color: #fff; border: none;}
                QPushButton {background-color: #4CAF50; color: #fff; border-radius: 10px; padding: 10px}
                QPushButton:hover {background-color: #3e8e41}
                QToolButton {background-color: #3a3b3e; border: none; border-radius: 10px; padding: 10px}
                QToolButton:hover {background-color: #444547}
                QLabel {font-size: 16px; font-weight: bold; color: #fff;}
            """)


    def on_button_clicked(self):
        command = self.line_edit.text()
        self.add_message("Vous", command)
        self.line_edit.clear()
        runnable = RunCoroutine(self.run_handle_command(command))
        QThreadPool.globalInstance().start(runnable)

    async def run_handle_command(self, command):
        try:
            task = asyncio.create_task(self.handle_command(command))
            task.add_done_callback(lambda task: self.add_response(task.result()))
            await task
        except Exception as e:
            print(f"Error: {e}")

    async def handle_command(self, command):
        print("en attente")
        resp = await anthony_ai(command)
        print("done")
        if resp:
            return resp
        else:
            return "No response from Anthony"

    def add_response(self, resp):
        if isinstance(resp, str):  # si la réponse est une chaîne de caractères
            self.chat_text_edit.append(f"<b>Anthony</b>: {resp}<br>")
        elif isinstance(resp, PIL.Image.Image):  # si la réponse est une image PIL
            qim = ImageQt.ImageQt(resp)
            pixmap = QPixmap.fromImage(qim)
            label = QLabel()
            label.setPixmap(pixmap)
            self.chat_layout.addWidget(label)
        elif isinstance(resp, bytes) or isinstance(resp, bytearray):  # si la réponse est des données binaires
            pixmap = QPixmap()
            pixmap.loadFromData(resp)
            label = QLabel()
            label.setPixmap(pixmap)
            self.chat_layout.addWidget(label)
        else:
            print(f"Réponse non prise en charge : {type(resp)}")

    def add_message(self, sender, message):
        self.chat_text_edit.append(f"<b>{sender}</b>: ")
        self.type_out_response(message)
        self.chat_text_edit.append("<br>")
        self.chat_text_edit.moveCursor(QTextCursor.End)

    def type_out_response(self, response):
        if response is not None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.append_char(response))
            self.timer.start(5)
            self.response_index = 0

        else:
            print("Response is None")
            

    def append_char(self, response):
        if self.response_index < len(response):
            self.chat_text_edit.insertPlainText(response[self.response_index])
            self.response_index += 1
            self.chat_text_edit.ensureCursorVisible()
            self.timer.start(10)
        else:
            self.timer.stop()

def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()