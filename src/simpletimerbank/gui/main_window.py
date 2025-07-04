"""Main window for the SimpleTimerBank application.

This module provides the main application window, which assembles all
the GUI components and connects them to the core business logic.
"""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QFontDatabase, QColor, QPalette, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QStatusBar,
    QFrame,
    QHBoxLayout,
)
import os

from simpletimerbank.core.app_state import AppStateManager
from simpletimerbank.core.countdown_timer import TimerState
from simpletimerbank.gui.widgets.time_display import TimeDisplayWidget
from simpletimerbank.gui.widgets.time_edit import TimeEditWidget
from simpletimerbank.gui.widgets.timer_control import TimerControlWidget


class MainWindow(QMainWindow):
    """The main application window for SimpleTimerBank.
    
    This class sets up the main window, lays out all the custom widgets,
    and handles the integration between the GUI and the AppStateManager.
    """
    
    def __init__(self, app_manager: AppStateManager, parent: QWidget = None) -> None:
        """Initialize the MainWindow.
        
        Parameters
        ----------
        app_manager : AppStateManager
            The application state manager instance.
        parent : QWidget, optional
            The parent widget, by default None.
        """
        super().__init__(parent)
        self._app_manager = app_manager
        
        # Window configuration
        self.setWindowTitle("Time Bank - Manage Your Time Assets")
        self.setFixedSize(500, 650)  # Increased height for additional explanations
        
        # Load custom font
        font_family = self._load_custom_font()
        
        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Bank Balance Section ---
        balance_section = QVBoxLayout()
        
        # Bank balance header with explanation
        bank_header_layout = QVBoxLayout()
        bank_header = QLabel("Your Time Bank Balance", self)
        bank_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        bank_explanation = QLabel("This is your available time. You can deposit or withdraw time using the controls below.", self)
        bank_explanation.setWordWrap(True)
        bank_explanation.setStyleSheet("font-size: 11px; color: #666;")
        
        bank_header_layout.addWidget(bank_header)
        bank_header_layout.addWidget(bank_explanation)
        balance_section.addLayout(bank_header_layout)
        
        self._time_display = TimeDisplayWidget(self, font_family=font_family)
        balance_section.addWidget(self._time_display)
        main_layout.addLayout(balance_section)
        
        # Add separator
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # --- Timer Countdown Section ---
        withdrawal_section = QVBoxLayout()
        
        timer_header = QLabel("Active Time Withdrawal", self)
        timer_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px; margin-bottom: 5px;")
        withdrawal_section.addWidget(timer_header)
        
        self._timer_countdown_label = QLabel("00:00:00", self)
        timer_font = QFont(font_family, 36, QFont.Weight.Bold)  # Use same font as bank balance
        self._timer_countdown_label.setFont(timer_font)
        self._timer_countdown_label.setStyleSheet("""
            color: #4CAF50;
            background-color: #1E1E1E;
            border: 2px solid #4A4A4A;
            border-radius: 10px;
            padding: 10px;
        """)
        self._timer_countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        withdrawal_section.addWidget(self._timer_countdown_label)
        
        # Overdraft indicator
        self._overdraft_indicator = QLabel("", self)
        self._overdraft_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._overdraft_indicator.setStyleSheet("font-weight: bold; color: #FF4500; font-size: 12px;")
        self._overdraft_indicator.setVisible(False)
        withdrawal_section.addWidget(self._overdraft_indicator)
        
        main_layout.addLayout(withdrawal_section)

        # --- Timer Controls and Duration Settings ---
        self._timer_control = TimerControlWidget(self)
        main_layout.addWidget(self._timer_control)
        
        self._time_edit = TimeEditWidget(self)
        main_layout.addWidget(self._time_edit)
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready. Set an amount and start a withdrawal.")
        
        # State tracking
        self._is_overdrafting = False
        
        # Setup timer for regular ticks
        self._setup_timer()
        
        # Connect signals and slots
        self._connect_signals()
        
        # Set initial state from AppManager
        self._update_ui_from_manager()

    def _load_custom_font(self) -> str:
        """Load custom font and return its family name."""
        font_family = "Courier New"
        font_paths = [
            "assets/fonts/DSEG7-Classic-Bold.ttf",
            os.path.join(os.path.dirname(__file__), "../../../assets/fonts/DSEG7-Classic-Bold.ttf"),
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        return families[0]
        return font_family
    
    def _setup_timer(self) -> None:
        """Set up the Qt timer for regular timer ticks."""
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._handle_timer_tick)
        self._app_manager.set_qt_timer(self._timer)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to appropriate handler methods."""
        # Note: We no longer connect the TimeEditWidget signals to the bank.
        # It's now used to get duration when starting a timer.
        self._time_edit.add_time_requested.connect(self._handle_add_time_to_bank)
        self._time_edit.set_time_requested.connect(self._handle_set_bank_time)
        self._time_edit.subtract_time_requested.connect(self._handle_subtract_time_from_bank)

        # Timer control signals
        self._timer_control.start_requested.connect(self._handle_start_timer)
        self._timer_control.pause_requested.connect(self._handle_pause_timer)
        self._timer_control.stop_requested.connect(self._handle_stop_timer)
        
        # App manager callbacks
        self._app_manager.set_timer_callback(self._on_timer_tick)
        self._app_manager.set_timer_completion_callback(self._on_timer_completion)
    
    def _update_ui_from_manager(self) -> None:
        """Update the entire UI based on the current AppManager state."""
        # Update bank balance display
        balance_formatted = self._app_manager.get_balance_formatted()
        self._time_display.update_time(balance_formatted)
        
        # Update timer countdown display
        timer_state = self._app_manager.get_timer_state()
        if timer_state in (TimerState.RUNNING, TimerState.PAUSED):
            # Get remaining seconds using the appropriate method
            remaining_seconds = self._app_manager._app_state.get_countdown_timer().get_remaining_seconds()
            self._timer_countdown_label.setText(self._format_time(remaining_seconds))
            
            # Update overdraft state
            self._is_overdrafting = self._app_manager.is_overdrafting()
            self._overdraft_indicator.setVisible(self._is_overdrafting)
            if self._is_overdrafting:
                self._overdraft_indicator.setText("OVERDRAFT ACTIVE - WITHDRAWING FROM YOUR BANK")
            else:
                self._overdraft_indicator.setText("")
        else:
            self._timer_countdown_label.setText("00:00:00")
            self._is_overdrafting = False
            self._overdraft_indicator.setVisible(False)
            
        # Update button and status states
        self._timer_control.update_button_states(timer_state)
        self._update_status_message(timer_state)

    def _update_status_message(self, state: TimerState) -> None:
        """Update the status bar message based on timer state."""
        if state == TimerState.IDLE:
            self.statusBar.showMessage("Ready. Set an amount and start a withdrawal.")
            self._timer_countdown_label.setStyleSheet("""
                color: #4CAF50;
                background-color: #1E1E1E;
                border: 2px solid #4A4A4A;
                border-radius: 10px;
                padding: 10px;
            """)
        elif state == TimerState.RUNNING:
            if self._is_overdrafting:
                self.statusBar.showMessage("Overdraft Mode: Withdrawing from your bank balance")
                self._timer_countdown_label.setStyleSheet("""
                    color: #FFFFFF;
                    background-color: #8B0000;
                    border: 2px solid #FF4500;
                    border-radius: 10px;
                    padding: 10px;
                """)
            else:
                self.statusBar.showMessage("Withdrawal in progress")
                self._timer_countdown_label.setStyleSheet("""
                    color: #4CAF50;
                    background-color: #1E1E1E;
                    border: 2px solid #4A4A4A;
                    border-radius: 10px;
                    padding: 10px;
                """)
        elif state == TimerState.PAUSED:
            self.statusBar.showMessage("Withdrawal paused")
            self._timer_countdown_label.setStyleSheet("""
                color: #FFA500;
                background-color: #1E1E1E;
                border: 2px solid #4A4A4A;
                border-radius: 10px;
                padding: 10px;
            """)
        elif state == TimerState.STOPPED:
            self.statusBar.showMessage("Withdrawal stopped. Remaining time returned to your balance.")
            self._is_overdrafting = False
            self._timer_countdown_label.setStyleSheet("""
                color: #4CAF50;
                background-color: #1E1E1E;
                border: 2px solid #4A4A4A;
                border-radius: 10px;
                padding: 10px;
            """)

    def _handle_add_time_to_bank(self, seconds: int):
        self._app_manager.add_time(seconds)
        self.statusBar.showMessage(f"Deposited {self._format_time(seconds)} to your bank balance.", 3000)
        self._update_ui_from_manager()

    def _handle_subtract_time_from_bank(self, seconds: int):
        try:
            self._app_manager.get_time_bank().withdraw(seconds)
            self.statusBar.showMessage(f"Withdrew {self._format_time(seconds)} from your bank balance.", 3000)
        except ValueError as e:
            QMessageBox.warning(self, "Insufficient Balance", str(e))
        self._update_ui_from_manager()
    
    def _handle_set_bank_time(self, seconds: int):
        try:
            self._app_manager.set_balance(seconds)
            self.statusBar.showMessage(f"Set bank balance to {self._format_time(seconds)}", 3000)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Time", str(e))
        self._update_ui_from_manager()
        
    def _handle_start_timer(self) -> None:
        """Handle request to start or resume the timer."""
        timer_state = self._app_manager.get_timer_state()

        if timer_state == TimerState.PAUSED:
            self._app_manager.resume_timer()
            self.statusBar.showMessage("Withdrawal resumed", 3000)
        else:
            duration = self._time_edit.get_duration_seconds()
            if duration <= 0:
                QMessageBox.warning(self, "Invalid Duration", "Please set a withdrawal amount greater than zero.")
                return
            
            if not self._app_manager.start_timer(duration):
                QMessageBox.warning(self, "Insufficient Balance", "Not enough time in your bank for this withdrawal.")
                return
            
            self.statusBar.showMessage(f"Started withdrawal of {self._format_time(duration)}", 3000)
        
        self._timer.start()
        self._update_ui_from_manager()
    
    def _handle_pause_timer(self) -> None:
        """Handle request to pause the timer."""
        self._app_manager.pause_timer()
        self.statusBar.showMessage("Withdrawal paused", 3000)
        self._update_ui_from_manager()
    
    def _handle_stop_timer(self) -> None:
        """Handle request to stop the timer."""
        self._app_manager.stop_timer()
        self._is_overdrafting = False
        self.statusBar.showMessage("Withdrawal cancelled. Remaining time returned to your balance.", 3000)
        self._timer.stop()
        self._update_ui_from_manager()
    
    def _handle_timer_tick(self) -> None:
        """Handle timer tick from QTimer."""
        if self._app_manager.get_timer_state() == TimerState.RUNNING:
            # Direct access to app_state.tick_timer() is not ideal but works for now
            self._app_manager._app_state.tick_timer()
            self._update_ui_from_manager()
    
    def _on_timer_tick(self, remaining_seconds: int) -> None:
        """Update the UI on each timer tick."""
        # This callback now drives the UI update
        self._update_ui_from_manager()
        
    def _on_timer_completion(self) -> None:
        """Handle timer completion event."""
        self.statusBar.showMessage("Withdrawal complete - Now in overdraft mode!", 5000)
        QMessageBox.warning(self, "Overdraft Mode Activated", 
                           "Your planned withdrawal time has been used up! You are now in overdraft mode.\n\n"
                           "The additional time will be withdrawn directly from your bank balance.")
        
    def _format_time(self, total_seconds: int) -> str:
        """Format seconds as HH:MM:SS string.
        
        Parameters
        ----------
        total_seconds : int
            Total number of seconds to format.
            
        Returns
        -------
        str
            Formatted time string.
        """
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.
        
        This method ensures application state is saved when the window is closed.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event.
        """
        print("Shutting down and saving state...")
        self._app_manager.shutdown()
        event.accept() 