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
        
        # Define styles
        self._normal_style = """
            color: #FFD700;
            background-color: #1E1E1E;
            border: 2px solid #4A4A4A;
            border-radius: 10px;
            padding: 10px;
        """
        
        self._overdraft_style = """
            color: #FFFFFF;
            background-color: #8B0000;
            border: 2px solid #FF4500;
            border-radius: 10px;
            padding: 10px;
        """
        
        # Set initial style
        self._time_label.setStyleSheet(self._normal_style)
        
        # Create a mode label to indicate overdraft
        self._mode_label = QLabel("NORMAL MODE", self)
        self._mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_label.setStyleSheet("font-weight: bold; color: #4A4A4A;")
        
        # Add widgets to layout
        layout.addWidget(self._time_label)
        layout.addWidget(self._mode_label)
        self.setLayout(layout)
        
        # Track overdraft state
        self._is_overdraft_mode = False
    
    def update_time(self, formatted_time: str) -> None:
        """Update the time displayed on the widget.
        
        Parameters
        ----------
        formatted_time : str
            The time string to display, e.g., "HH:MM:SS".
        """
        self._time_label.setText(formatted_time)
    
    def set_overdraft_mode(self, is_overdraft: bool) -> None:
        """Set whether the display is in overdraft mode.
        
        In overdraft mode, the display uses a different color scheme to
        visually indicate that the user is now withdrawing from their balance.
        
        Parameters
        ----------
        is_overdraft : bool
            Whether the display should be in overdraft mode.
        """
        if is_overdraft == self._is_overdraft_mode:
            return  # No change needed
            
        self._is_overdraft_mode = is_overdraft
        
        if is_overdraft:
            self._time_label.setStyleSheet(self._overdraft_style)
            self._mode_label.setText("OVERDRAFT MODE")
            self._mode_label.setStyleSheet("font-weight: bold; color: #FF4500;")
        else:
            self._time_label.setStyleSheet(self._normal_style)
            self._mode_label.setText("NORMAL MODE")
            self._mode_label.setStyleSheet("font-weight: bold; color: #4A4A4A;") 