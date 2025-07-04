"""Application state management module.

This module contains the AppStateManager class responsible for coordinating
state across all application components and managing the application lifecycle.
"""

from typing import Callable, Optional, TYPE_CHECKING

from .time_balance import TimeBalance
from .countdown_timer import CountdownTimer, TimerState
from .persistence import PersistenceService

if TYPE_CHECKING:
    pass


class AppStateManager:
    """Manages application state for the SimpleTimerBank application.
    
    This class coordinates state between TimeBalance, CountdownTimer, and
    PersistenceService components, and handles application lifecycle events.
    """
    
    def __init__(self) -> None:
        """Initialize AppStateManager with default components."""
        # Initialize core components
        self._time_balance = TimeBalance()
        self._persistence_service = PersistenceService()
        self._countdown_timer = CountdownTimer(self._time_balance)
        
        # State tracking
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize application state and load saved data."""
        if self._initialized:
            return
        
        # Load saved data from persistence
        saved_data = self._persistence_service.load_data()
        
        # Restore time balance if available
        if "balance_seconds" in saved_data:
            balance_seconds = saved_data["balance_seconds"]
            # Validate balance is non-negative
            if isinstance(balance_seconds, (int, float)) and balance_seconds >= 0:
                # Reset balance to zero first, then add the saved amount
                self._time_balance = TimeBalance()
                self._time_balance.add_time(int(balance_seconds))
                # Update countdown timer reference
                self._countdown_timer = CountdownTimer(self._time_balance)
        
        self._initialized = True
    
    def shutdown(self) -> None:
        """Shutdown application and save current state."""
        # Stop any running timer
        self._countdown_timer.stop()
        
        # Prepare data to save
        save_data = {
            "balance_seconds": self._time_balance.get_balance_seconds(),
        }
        
        # Save current state
        try:
            self._persistence_service.save_data(save_data)
        except Exception:
            # Handle save failures gracefully - don't crash on shutdown
            pass
    
    def get_time_balance(self) -> TimeBalance:
        """Get reference to the time balance manager.
        
        Returns
        -------
        TimeBalance
            Reference to TimeBalance instance.
        """
        return self._time_balance
    
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
    
    # Convenience methods for common operations
    
    def add_time(self, seconds: int) -> None:
        """Add time to the balance.
        
        Parameters
        ----------
        seconds : int
            Number of seconds to add to the balance.
            
        Raises
        ------
        ValueError
            If seconds is negative.
        """
        self._time_balance.add_time(seconds)
    
    def set_balance(self, seconds: int) -> None:
        """Set the time balance to an absolute value.
        
        Parameters
        ----------
        seconds : int
            The total number of seconds to set the balance to.
            
        Raises
        ------
        ValueError
            If seconds is negative.
        """
        self._time_balance.set_balance(seconds)
    
    def get_balance_seconds(self) -> int:
        """Get current balance in seconds.
        
        Returns
        -------
        int
            Current time balance in seconds.
        """
        return self._time_balance.get_balance_seconds()
    
    def get_balance_formatted(self) -> str:
        """Get current balance as formatted string.
        
        Returns
        -------
        str
            Current balance formatted as HH:MM:SS.
        """
        return self._time_balance.get_balance_formatted()
    
    def start_timer(self) -> bool:
        """Start the countdown timer.
        
        Returns
        -------
        bool
            True if timer started successfully, False if insufficient balance.
        """
        return self._countdown_timer.start()
    
    def pause_timer(self) -> None:
        """Pause the countdown timer."""
        self._countdown_timer.pause()
    
    def stop_timer(self) -> None:
        """Stop the countdown timer."""
        self._countdown_timer.stop()
    
    def get_timer_state(self) -> TimerState:
        """Get current timer state.
        
        Returns
        -------
        TimerState
            Current state of the timer.
        """
        return self._countdown_timer.get_state()
    
    def set_timer_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback function to be called every timer tick.
        
        Parameters
        ----------
        callback : Callable[[int], None]
            Function to call with remaining seconds on each tick.
        """
        self._countdown_timer.set_tick_callback(callback) 