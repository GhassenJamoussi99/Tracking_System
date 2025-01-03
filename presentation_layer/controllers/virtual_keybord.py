from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLineEdit
from PyQt6.QtCore import QSize
import logging

class CustomLineEdit(QLineEdit):
    """
    @class CustomLineEdit
    @brief A custom QLineEdit that shows a virtual keyboard on mouse press.
    """
    def __init__(self, parent=None):
        """
        @brief Constructor for CustomLineEdit.
        @param parent The parent widget, if any.
        """
        super().__init__(parent)
        self.keyboard = None  # To store reference to the virtual keyboard

    def mousePressEvent(self, event):
        """
        @brief Event handler for mouse press events.
        @param event The mouse press event.
        """
        super().mousePressEvent(event)
        if self.keyboard:
            self.keyboard.show()

class VirtualKeyboard(QWidget):
    """
    @class VirtualKeyboard
    @brief A virtual keyboard widget that can be used for text input.
    """
    def __init__(self, target_input, mode='numeric'):
        """
        @brief Constructor for VirtualKeyboard.
        @param target_input The input widget that the keyboard will send input to.
        @param mode The mode of the keyboard ('numeric' or 'full').
        """
        super().__init__()
        self.target_input = target_input
        self.is_shift = False
        self.mode = mode  # 'numeric' or 'full'
        self.initUI()

    def initUI(self):
        """
        @brief Initializes the UI of the virtual keyboard.
        """
        self.layout = QGridLayout()
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(3, 3, 3, 8)
        self.setLayout(self.layout)
        self.setStyleSheet("background-color: #1E1E1E;")
        self.load_keyboard()

    def load_keyboard(self):
        """
        @brief Loads the keyboard layout based on the current mode.
        """
        self.clear_layout(self.layout)

        if self.mode == 'numeric':
            buttons = [
                ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
                ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
                ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
                ('Clear', 3, 0), ('0', 3, 1), ('Enter', 3, 2),
            ]
        else:
            buttons = [
                ('1', 0, 0), ('2', 0, 1), ('3', 0, 2), ('4', 0, 3), ('5', 0, 4),
                ('6', 0, 5), ('7', 0, 6), ('8', 0, 7), ('9', 0, 8), ('0', 0, 9),
                ('Q', 1, 0), ('W', 1, 1), ('E', 1, 2), ('R', 1, 3), ('T', 1, 4),
                ('Y', 1, 5), ('U', 1, 6), ('I', 1, 7), ('O', 1, 8), ('P', 1, 9),
                ('A', 2, 0), ('S', 2, 1), ('D', 2, 2), ('F', 2, 3), ('G', 2, 4),
                ('H', 2, 5), ('J', 2, 6), ('K', 2, 7), ('L', 2, 8), 
                ('Shift', 3, 0), ('Z', 3, 1), ('X', 3, 2), ('C', 3, 3), ('V', 3, 4),
                ('B', 3, 5), ('N', 3, 6), ('M', 3, 7), ('Backspace', 3, 8),
                ('123', 4, 0), ('Space', 4, 1, 1, 3), ('Clear', 4, 4), ('Enter', 4, 5)
            ]

        for item in buttons:
            if len(item) == 3:
                text, row, col = item
                row_span = col_span = 1
            elif len(item) == 5:
                text, row, col, row_span, col_span = item
            button = QPushButton(text)
            button.setFixedSize(QSize(60, 60))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #FFFFFF;
                    border-radius: 5px;
                    font-size: 16px;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
            """)
            button.clicked.connect(lambda state, text=text: self.on_button_click(text))
            self.layout.addWidget(button, row, col, row_span, col_span)

    def clear_layout(self, layout):
        """
        @brief Clears all widgets from the given layout.
        @param layout The layout to clear.
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_button_click(self, text):
        """
        @brief Handles button click events on the virtual keyboard.
        @param text The text of the button that was clicked.
        """
        if text == 'Clear':
            self.target_input.clear()
        elif text == 'Enter':
            logging.info("Input entered: {}".format(self.target_input.text()))
            self.hide()
        elif text == 'Backspace':
            current_text = self.target_input.text()
            self.target_input.setText(current_text[:-1])
        elif text == 'Shift':
            self.is_shift = not self.is_shift
        elif text == 'Space':
            self.target_input.insert(' ')
        elif text == '123':
            self.mode = 'numeric'
            self.load_keyboard()
        else:
            if self.is_shift:
                self.target_input.insert(text.upper())
            else:
                self.target_input.insert(text.lower())
            if self.is_shift:
                self.is_shift = False