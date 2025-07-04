"""Time display widget for SimpleTimerBank.

This module provides a widget to display the time balance in a visually
appealing format, like a digital clock.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class TimeDisplayWidget(QWidget):
    """A widget to display the time balance using a large QLabel.
    
    This widget provides a visually clear, non-editable display of the
    current time balance, formatted as HH:MM:SS.
    """
    
    def __init__(self, parent: QWidget = None, font_family: str = "Courier New") -> None:
        """Initialize the TimeDisplayWidget.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget, by default None.
        font_family : str
            The font family to use for the display.
        """
        super().__init__(parent)
        
        # Create the main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create the time display label
        self._time_label = QLabel("00:00:00", self)
        font = QFont(font_family, 60, QFont.Weight.Bold)  # Reduced font size
        self._time_label.setFont(font)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_label.setStyleSheet("""
            color: #FFD700;
            background-color: #1E1E1E;
            border: 2px solid #4A4A4A;
            border-radius: 10px;
            padding: 10px;
        """)
        
        layout.addWidget(self._time_label)
        self.setLayout(layout)
    
    def update_time(self, formatted_time: str) -> None:
        """Update the time displayed on the widget.
        
        Parameters
        ----------
        formatted_time : str
            The time string to display, e.g., "HH:MM:SS".
        """
        self._time_label.setText(formatted_time) 