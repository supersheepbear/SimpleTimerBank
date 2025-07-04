"""Application state management module.

This module contains the AppState class responsible for coordinating
state across all application components and managing the application lifecycle.
"""

from typing import Callable, Optional, Dict, Any

from .time_bank import TimeBank
from .countdown_timer import CountdownTimer, TimerState
from .persistence import PersistenceService
from .notification_service import NotificationService


class AppState:
    """Manages application state for the SimpleTimerBank application.
    
    This class orchestrates the interaction between TimeBank and CountdownTimer,
    handling session management, timer callbacks, and persistence.
    """
    
    def __init__(self) -> None:
        """Initialize AppState with default components."""
        # Initialize core components
        self._time_bank = TimeBank()
        self._countdown_timer = CountdownTimer()
        self._persistence_service = PersistenceService()
        self._notification_service = NotificationService()
        
        # Set up callback handlers
        self._countdown_timer.set_completion_callback(self._on_timer_completion)
        self._completion_callback: Optional[Callable[[], None]] = None
        self._tick_callback: Optional[Callable[[int], None]] = None
        
        # State tracking
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize application state and load saved data."""
        if self._initialized:
            return
        
        # Load saved data from persistence
        saved_data = self._persistence_service.load_data()
        
        # Restore time balance if available
        if "balance" in saved_data:
            balance_seconds = saved_data["balance"]
            # Validate balance is non-negative
            if isinstance(balance_seconds, (int, float)) and balance_seconds >= 0:
                self._time_bank.set_balance(int(balance_seconds))
        
        self._initialized = True
    
    def shutdown(self) -> None:
        """Shutdown application and save current state."""
        # Stop any running timer
        try:
            if self._countdown_timer.get_state() != TimerState.IDLE and \
               self._countdown_timer.get_state() != TimerState.STOPPED:
                self._countdown_timer.stop()
        except ValueError:
            # Ignore any errors when stopping timer during shutdown
            pass
        
        # Prepare data to save
        save_data = {
            "balance": self._time_bank.get_balance(),
        }
        
        # Save current state
        try:
            self._persistence_service.save_data(save_data)
        except Exception:
            # Handle save failures gracefully - don't crash on shutdown
            pass
    
    def get_time_bank(self) -> TimeBank:
        """Get reference to the time bank.
        
        Returns
        -------
        TimeBank
            Reference to TimeBank instance.
        """
        return self._time_bank
    
    def get_countdown_timer(self) -> CountdownTimer:
        """Get reference to the countdown timer.
        
        Returns
        -------
        CountdownTimer
            Reference to CountdownTimer instance.
        """
        return self._countdown_timer
    
    def get_persistence_service(self) -> PersistenceService:
        """Get reference to the persistence service.
        
        Returns
        -------
        PersistenceService
            Reference to PersistenceService instance.
        """
        return self._persistence_service
    
    def get_notification_service(self) -> NotificationService:
        """Get reference to the notification service.
        
        Returns
        -------
        NotificationService
            Reference to NotificationService instance.
        """
        return self._notification_service
    
    def start_session(self, duration_seconds: int) -> bool:
        """Start a new timer session with the specified duration.
        
        This withdraws time from the bank and starts the timer.
        
        Parameters
        ----------
        duration_seconds : int
            Duration of the session in seconds.
            
        Returns
        -------
        bool
            True if session started successfully, False if insufficient balance.
        """
        # Check if we have enough balance
        if self._time_bank.get_balance() < duration_seconds:
            return False
        
        try:
            # Withdraw time from bank
            self._time_bank.withdraw(duration_seconds)
            
            # Start the timer
            self._countdown_timer.start(duration_seconds)
            
            # Set up timer tick callback
            if self._tick_callback:
                self._countdown_timer.set_tick_callback(self._tick_callback)
                
            return True
        except ValueError:
            # If anything fails, ensure we don't lose the time
            return False
    
    def pause_session(self) -> None:
        """Pause the current timer session."""
        try:
            self._countdown_timer.pause()
        except ValueError:
            # Ignore errors if timer is not in the right state
            pass
    
    def resume_session(self) -> None:
        """Resume a paused timer session."""
        try:
            self._countdown_timer.resume()
        except ValueError:
            # Ignore errors if timer is not in the right state
            pass
    
    def stop_session(self) -> None:
        """Stop the current timer session.
        
        This will refund any remaining time to the bank if the timer
        has not entered overdraft mode.
        """
        # Get remaining seconds before stopping (for refund)
        timer = self._countdown_timer
        remaining_seconds = timer.get_remaining_seconds()
        is_overdrafting = timer.is_overdrafting()
        
        try:
            # Stop the timer
            timer.stop()
            
            # Only refund if not in overdraft mode
            if not is_overdrafting and remaining_seconds > 0:
                self._time_bank.deposit(remaining_seconds)
        except ValueError:
            # Ignore errors if timer is not in the right state
            pass
    
    def tick_timer(self) -> None:
        """Process a timer tick.
        
        This should be called by a timing mechanism (like a QTimer) at regular
        intervals (typically every second) when the timer is running.
        """
        # Call the timer's tick method
        overdraft_seconds = self._countdown_timer.tick()
        
        # Handle any overdraft signal
        if overdraft_seconds is not None:
            self._handle_overdraft_signal(overdraft_seconds)
    
    def _handle_overdraft_signal(self, seconds: int) -> None:
        """Handle an overdraft signal from the timer.
        
        This withdraws time from the bank and stops the timer if the bank
        is depleted.
        
        Parameters
        ----------
        seconds : int
            Number of seconds to withdraw from the bank.
        """
        try:
            # Try to withdraw the overdraft amount
            self._time_bank.withdraw(seconds)
        except ValueError:
            # If insufficient funds, withdraw what we can and stop
            bank_balance = self._time_bank.get_balance()
            if bank_balance > 0:
                self._time_bank.set_balance(0)
                
            # Notify user that bank is depleted
            self._notification_service.notify_bank_depleted()
            
            # Stop the timer
            try:
                self._countdown_timer.stop()
            except ValueError:
                # Ignore errors if timer is already stopped
                pass
    
    def _on_timer_completion(self) -> None:
        """Internal callback for timer completion.
        
        This is called when the timer reaches zero and enters overdraft mode.
        """
        # Send notification
        self._notification_service.notify_timer_completed()
        
        # Call user-provided callback if set
        if self._completion_callback:
            self._completion_callback()
    
    def set_timer_completion_callback(self, callback: Callable[[], None]) -> None:
        """Set callback function for timer completion.
        
        Parameters
        ----------
        callback : Callable[[], None]
            Function to call when timer completes initial countdown.
        """
        self._completion_callback = callback
    
    def set_timer_tick_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback function for timer ticks.
        
        Parameters
        ----------
        callback : Callable[[int], None]
            Function to call with remaining seconds on each tick.
        """
        self._tick_callback = callback
        if self._countdown_timer.get_state() != TimerState.IDLE:
            self._countdown_timer.set_tick_callback(callback)


class AppStateManager:
    """GUI-friendly wrapper for AppState that provides simplified methods
    for the user interface layer.
    
    This class serves as an interface between the GUI and the core application state,
    providing methods that map well to UI interactions.
    """
    
    def __init__(self) -> None:
        """Initialize AppStateManager with a new AppState instance."""
        self._app_state = AppState()
        self._qt_timer = None
    
    def initialize(self) -> None:
        """Initialize the application state and prepare for use."""
        self._app_state.initialize()
    
    def shutdown(self) -> None:
        """Shutdown the application and save state."""
        self._app_state.shutdown()
    
    def get_time_balance(self) -> TimeBank:
        """Get the time balance instance.
        
        Returns
        -------
        TimeBank
            The time balance instance.
        """
        return self._app_state.get_time_bank()
    
    def set_balance(self, seconds: int) -> None:
        """Set the time balance directly.
        
        Parameters
        ----------
        seconds : int
            New balance value in seconds.
        
        Raises
        ------
        ValueError
            If seconds is negative.
        """
        self._app_state.get_time_bank().set_balance(seconds)
    
    def add_time(self, seconds: int) -> None:
        """Add time to the balance.
        
        Parameters
        ----------
        seconds : int
            Amount of time to add in seconds.
        """
        self._app_state.get_time_bank().deposit(seconds)
    
    def get_balance_seconds(self) -> int:
        """Get the current time balance in seconds.
        
        Returns
        -------
        int
            Balance in seconds.
        """
        return self._app_state.get_time_bank().get_balance()
    
    def get_balance_formatted(self) -> str:
        """Get the current time balance formatted as HH:MM:SS.
        
        Returns
        -------
        str
            Formatted time string.
        """
        total_seconds = self.get_balance_seconds()
        
        # Format as HH:MM:SS
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def start_timer(self) -> bool:
        """Start the timer with the current balance.
        
        Returns
        -------
        bool
            True if timer started successfully, False otherwise.
        """
        duration = self.get_balance_seconds()
        return self._app_state.start_session(duration)
    
    def pause_timer(self) -> None:
        """Pause the timer."""
        self._app_state.pause_session()
    
    def stop_timer(self) -> None:
        """Stop the timer and refund any remaining time."""
        self._app_state.stop_session()
    
    def get_timer_state(self) -> TimerState:
        """Get the current timer state.
        
        Returns
        -------
        TimerState
            Current state of the timer.
        """
        return self._app_state.get_countdown_timer().get_state()
    
    def set_timer_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback function for timer ticks.
        
        Parameters
        ----------
        callback : Callable[[int], None]
            Function to call with remaining seconds on each tick.
        """
        self._app_state.set_timer_tick_callback(callback)
    
    def set_timer_completion_callback(self, callback: Callable[[], None]) -> None:
        """Set callback function for timer completion.
        
        Parameters
        ----------
        callback : Callable[[], None]
            Function to call when timer completes initial countdown.
        """
        self._app_state.set_timer_completion_callback(callback)
    
    def set_qt_timer(self, timer) -> None:
        """Set the QTimer instance used for timer ticks.
        
        Parameters
        ----------
        timer : QTimer
            The QTimer instance.
        """
        self._qt_timer = timer 