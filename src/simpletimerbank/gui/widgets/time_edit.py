"""Time editing widget for SimpleTimerBank.

This module provides a widget for users to add or subtract time
from their time balance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSpinBox,
    QPushButton,
    QLabel,
    QGroupBox,
)


class TimeEditWidget(QWidget):
    """A widget for editing the time balance.
    
    This widget provides spin boxes for hours, minutes, and seconds,
    along with "Add Time", "Subtract Time", and "Set Time" buttons. It emits signals
    when these buttons are clicked.
    """
    
    # Signals
    add_time_requested = Signal(int)  # Emits total seconds to add
    subtract_time_requested = Signal(int)  # Emits total seconds to subtract
    set_time_requested = Signal(int) # Emits total seconds to set
    
    def __init__(self, parent: QWidget = None) -> None:
        """Initialize the TimeEditWidget.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget, by default None.
        """
        super().__init__(parent)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Group box for the time editor
        group_box = QGroupBox("Modify Time Balance", self)
        group_layout = QGridLayout(group_box)
        
        # Spin boxes for H, M, S
        self._hours_spin = self._create_spinbox(0, 999)
        self._minutes_spin = self._create_spinbox(0, 59)
        self._seconds_spin = self._create_spinbox(0, 59)
        
        # Labels
        group_layout.addWidget(QLabel("Hours", self), 0, 0)
        group_layout.addWidget(QLabel("Minutes", self), 0, 1)
        group_layout.addWidget(QLabel("Seconds", self), 0, 2)
        
        group_layout.addWidget(self._hours_spin, 1, 0)
        group_layout.addWidget(self._minutes_spin, 1, 1)
        group_layout.addWidget(self._seconds_spin, 1, 2)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        self._add_button = QPushButton("Add Time", self)
        self._subtract_button = QPushButton("Subtract Time", self)
        self._set_button = QPushButton("Set Time", self)
        button_layout.addWidget(self._add_button)
        button_layout.addWidget(self._subtract_button)
        button_layout.addWidget(self._set_button)
        
        group_layout.addLayout(button_layout, 2, 0, 1, 3)
        
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)
        
        # Connect signals
        self._add_button.clicked.connect(self._on_add_clicked)
        self._subtract_button.clicked.connect(self._on_subtract_clicked)
        self._set_button.clicked.connect(self._on_set_clicked)
    
    def _create_spinbox(self, min_val: int, max_val: int) -> QSpinBox:
        """Helper to create and configure a QSpinBox."""
        spinbox = QSpinBox(self)
        spinbox.setRange(min_val, max_val)
        spinbox.setSingleStep(1)
        spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return spinbox
    
    def _get_total_seconds(self) -> int:
        """Calculate total seconds from spin boxes."""
        hours = self._hours_spin.value()
        minutes = self._minutes_spin.value()
        seconds = self._seconds_spin.value()
        return (hours * 3600) + (minutes * 60) + seconds
    
    def _on_add_clicked(self) -> None:
        """Handle add button click."""
        total_seconds = self._get_total_seconds()
        if total_seconds > 0:
            self.add_time_requested.emit(total_seconds)
    
    def _on_subtract_clicked(self) -> None:
        """Handle subtract button click."""
        total_seconds = self._get_total_seconds()
        if total_seconds > 0:
            self.subtract_time_requested.emit(total_seconds)

    def _on_set_clicked(self) -> None:
        """Handle set button click."""
        total_seconds = self._get_total_seconds()
        # Allow setting time to 0
        if total_seconds >= 0:
            self.set_time_requested.emit(total_seconds) 