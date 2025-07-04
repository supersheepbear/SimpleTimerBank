"""Main window for the SimpleTimerBank application.

This module provides the main application window, which assembles all
the GUI components and connects them to the core business logic.
"""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent, QFontDatabase
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
)

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
        self.setWindowTitle("Simple Timer Bank")
        self.setFixedSize(500, 450)
        
        # Load custom font if available
        # You would need to distribute the font file with the application
        # and place it in a known assets folder.
        font_path = "assets/fonts/DSEG7-Classic-Bold.ttf"
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = "DSEG7 Classic"
        if font_id == -1:
            print(f"Warning: Could not load custom font from {font_path}")
            font_family = "Courier New"  # Fallback font
        
        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create and add widgets
        self._time_display = TimeDisplayWidget(self, font_family=font_family)
        self._time_edit = TimeEditWidget(self)
        self._timer_control = TimerControlWidget(self)
        
        main_layout.addWidget(self._time_display)
        main_layout.addWidget(self._timer_control)
        main_layout.addWidget(self._time_edit)
        
        # Setup timer for regular ticks
        self._setup_timer()
        
        # Connect signals and slots
        self._connect_signals()
        
        # Set initial state from AppManager
        self._update_ui_from_manager()
    
    def _setup_timer(self) -> None:
        """Set up the Qt timer for regular timer ticks."""
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 1 second interval
        self._timer.timeout.connect(self._handle_timer_tick)
        self._timer.start()
        
        # Set the timer in the app manager
        self._app_manager.set_qt_timer(self._timer)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to appropriate handler methods."""
        # Time editing signals
        self._time_edit.add_time_requested.connect(self._handle_add_time)
        self._time_edit.subtract_time_requested.connect(self._handle_subtract_time)
        self._time_edit.set_time_requested.connect(self._handle_set_time)
        
        # Timer control signals
        self._timer_control.start_requested.connect(self._handle_start_timer)
        self._timer_control.pause_requested.connect(self._handle_pause_timer)
        self._timer_control.stop_requested.connect(self._handle_stop_timer)
        
        # App manager callbacks for timer ticks
        self._app_manager.set_timer_callback(self._on_timer_tick)
    
    def _update_ui_from_manager(self) -> None:
        """Update the entire UI based on the current AppManager state."""
        self._on_timer_tick(self._app_manager.get_balance_seconds())
        self._timer_control.update_button_states(self._app_manager.get_timer_state())
    
    def _handle_add_time(self, seconds: int) -> None:
        """Handle request to add time.
        
        Parameters
        ----------
        seconds : int
            Number of seconds to add to the balance.
        """
        self._app_manager.add_time(seconds)
        self._update_ui_from_manager()
    
    def _handle_set_time(self, seconds: int) -> None:
        """Handle request to set the time balance directly.
        
        Parameters
        ----------
        seconds : int
            New balance value in seconds.
        """
        try:
            self._app_manager.set_balance(seconds)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Time", str(e))
        self._update_ui_from_manager()
    
    def _handle_subtract_time(self, seconds: int) -> None:
        """Handle request to subtract time.
        
        Parameters
        ----------
        seconds : int
            Number of seconds to subtract from the balance.
        """
        current_balance = self._app_manager.get_balance_seconds()
        if seconds > current_balance:
            QMessageBox.warning(
                self,
                "Insufficient Balance",
                "Cannot subtract more time than is available in the balance.",
            )
        else:
            try:
                # Get the time bank and subtract time directly
                self._app_manager.get_time_balance().withdraw(seconds)
                self._update_ui_from_manager()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def _handle_start_timer(self) -> None:
        """Handle request to start or resume the timer."""
        if self._app_manager.get_balance_seconds() <= 0:
            QMessageBox.warning(
                self, "No Time", "Cannot start timer with zero balance."
            )
            return
            
        if self._app_manager.get_timer_state() == TimerState.PAUSED:
            # Resume if paused
            self._app_manager.pause_timer()
        else:
            # Start new session with current balance
            if not self._app_manager.start_timer():
                QMessageBox.warning(
                    self, "Start Failed", "Failed to start timer session."
                )
                return
        
        self._update_ui_from_manager()
    
    def _handle_pause_timer(self) -> None:
        """Handle request to pause the timer."""
        self._app_manager.pause_timer()
        self._update_ui_from_manager()
    
    def _handle_stop_timer(self) -> None:
        """Handle request to stop the timer."""
        self._app_manager.stop_timer()
        self._update_ui_from_manager()
    
    def _handle_timer_tick(self) -> None:
        """Handle timer tick from QTimer."""
        if self._app_manager.get_timer_state() == TimerState.RUNNING:
            self._app_manager._app_state.tick_timer()
            self._update_ui_from_manager()
    
    def _on_timer_tick(self, remaining_seconds: int) -> None:
        """Update the UI on each timer tick.
        
        Parameters
        ----------
        remaining_seconds : int
            Remaining seconds in the timer.
        """
        formatted_time = self._app_manager.get_balance_formatted()
        self._time_display.update_time(formatted_time)
        
        # Also update button states as timer might stop on its own
        self._timer_control.update_button_states(self._app_manager.get_timer_state())
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the window close event.
        
        Ensures the application state is saved before closing.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event object.
        """
        print("Shutting down and saving state...")
        self._app_manager.shutdown()
        event.accept() 