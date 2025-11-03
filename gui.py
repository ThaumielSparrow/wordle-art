from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QDateEdit, QMessageBox
)

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QMouseEvent
import random

import wordle

# Custom QPushButton with different RClick/LClick bindings
class RLButton(QPushButton):
    leftClicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftClicked.emit()
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit()
        
        super().mousePressEvent(event)

# GUI main class
class WordleGUI(QMainWindow):
    COLORS = ["#787c7e", "#3cB043", "#ffff00"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wordle Art Generator")

        self.grid_buttons = []
        self.grid_states = [[0]*5 for _ in range(6)]
        self.word_list = wordle.load_word_list()

        if not self.word_list:
            QMessageBox.critical(self, "Error", f"Could not load word list from {wordle.WORD_LIST}.\nPlease make sure the file exists.")
            self.close()
            return

        self.init_ui()
    
    
    def init_ui(self):
        # Main Layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)

        # Inputs
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Select Date:"))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("yyyy-MM-dd")
        self.date_picker.setDate(QDate.currentDate())
        input_layout.addWidget(self.date_picker)

        fetch_btn = QPushButton("Fetch")
        fetch_btn.clicked.connect(self.fetch_word)
        input_layout.addWidget(fetch_btn)

        input_layout.addStretch()

        input_layout.addWidget(QLabel("Answer:"))
        self.answer_entry = QLineEdit()
        self.answer_entry.setFixedWidth(80)
        self.answer_entry.setFont(QFont("Arial", 12))
        self.answer_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.answer_entry)

        main_layout.addLayout(input_layout)
    
        # Grid Selection
        grid_layout = QGridLayout()
        grid_layout.setSpacing(3)
        for r in range(6):
            row_buttons = []
            for c in range(5):
                btn = RLButton()
                btn.setFixedSize(50, 50)
                btn.setStyleSheet(f"background-color: {self.COLORS[0]}; border-radius: 5px;")

                # Connect to handlers
                btn.leftClicked.connect(lambda r=r, c=c: self.toggle_square(r,c))
                btn.rightClicked.connect(lambda r=r, c=c: self.reset_square(r,c))

                grid_layout.addWidget(btn, r, c)
                row_buttons.append(btn)
            
            self.grid_buttons.append(row_buttons)
        
        grid_container_layout = QHBoxLayout()
        grid_container_layout.addStretch(1)
        grid_container_layout.addLayout(grid_layout)
        grid_container_layout.addStretch(1)

        main_layout.addLayout(grid_container_layout)

        # Controls
        control_layout = QHBoxLayout()
        control_layout.addStretch()

        generate_btn = QPushButton("Generate Guesses")
        generate_btn.clicked.connect(self.generate_guesses)
        control_layout.addWidget(generate_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_interface)
        control_layout.addWidget(reset_btn)

        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # Results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Courier", 11))
        self.result_text.setFixedHeight(125)
        self.result_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.result_text)


    def fetch_word(self):
        date_str = self.date_picker.date().toString("yyyy-MM-dd")
        answer = wordle.get_wordle_answer(date_str)
        if answer:
            self.answer_entry.setText(answer.upper())
        else:
            self.answer_entry.clear()
            QMessageBox.warning(self, "Fetch Failed", f"Could not retrieve the NYT Wordle answer for date: {date_str}.")

    
    def toggle_square(self, r, c):
        new_state = (self.grid_states[r][c] + 1) % 3
        self.grid_states[r][c] = new_state
        self.grid_buttons[r][c].setStyleSheet(f"background-color: {self.COLORS[new_state]}; border-radius: 5px;")


    def reset_square(self, r, c):
        self.grid_states[r][c] = 0
        self.grid_buttons[r][c].setStyleSheet(f"background-color: {self.COLORS[0]}; border-radius: 5px;")


    def generate_guesses(self):
        answer = self.answer_entry.text().strip().upper()

        if len(answer) != 5 or answer not in self.word_list:
            QMessageBox.critical(self, "Invalid Input", "Please enter or fetch a valid 5-letter word as the answer.")
            return

        found_guesses = wordle.find_art_guesses(self.grid_states, answer, self.word_list)
        self.result_text.clear()
        for i, guess in enumerate(found_guesses):
            self.result_text.append(guess if guess else "Can't match pattern")
        # Introduce some variety between generations
        random.shuffle(self.word_list)


    def reset_interface(self):
        for r in range(6):
            for c in range(5):
                self.reset_square(r, c)
        
        self.result_text.clear()