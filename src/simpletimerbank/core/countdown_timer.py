"""Countdown timer management module.

This module contains the CountdownTimer class responsible for managing
the countdown timer functionality that consumes time balance.
"""

import threading
from enum import Enum
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .time_balance import TimeBalance


class TimerState(Enum):
    """Enumeration of possible timer states."""
    STOPPED = "stopped"
    RUNNING = "running" 
    PAUSED = "paused"


class CountdownTimer:
    """Manages countdown timer operations for the SimpleTimerBank application.
    
    This class handles starting, pausing, stopping the countdown timer
    and coordinating with the TimeBalance to consume time.
    """
    
    def __init__(self, time_balance: Optional["TimeBalance"] = None) -> None:
        """Initialize CountdownTimer.
        
        Parameters
        ----------
        time_balance : TimeBalance, optional
            Reference to the time balance manager.
        """
        self._time_balance = time_balance
        self._state = TimerState.STOPPED
        self._timer: Optional[threading.Timer] = None
        self._tick_callback: Optional[Callable[[int], None]] = None
    
    def start(self) -> bool:
        """Start the countdown timer.
        
        Returns
        -------
        bool
            True if timer started successfully, False if insufficient balance.
        """
        # If already running, don't start again
        if self._state == TimerState.RUNNING:
            return False
        
        # Check if we have a time balance and it has time
        if self._time_balance is None:
            return False
        
        if self._time_balance.get_balance_seconds() <= 0:
            return False
        
        # If we were paused, resume; otherwise start fresh
        self._state = TimerState.RUNNING
        self._schedule_next_tick()
        return True
    
    def pause(self) -> None:
        """Pause the countdown timer."""
        if self._state == TimerState.RUNNING:
            self._state = TimerState.PAUSED
            self._cancel_timer()
    
    def stop(self) -> None:
        """Stop the countdown timer and reset."""
        self._state = TimerState.STOPPED
        self._cancel_timer()
    
    def get_state(self) -> TimerState:
        """Get current timer state.
        
        Returns
        -------
        TimerState
            Current state of the timer.
        """
        return self._state
    
    def set_tick_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback function to be called every timer tick.
        
        Parameters
        ----------
        callback : Callable[[int], None]
            Function to call with remaining seconds on each tick.
        """
        self._tick_callback = callback
    
    def get_remaining_seconds(self) -> int:
        """Get remaining time in seconds.
        
        Returns
        -------
        int
            Remaining time in seconds, or 0 if no time balance.
        """
        if self._time_balance is None:
            return 0
        return self._time_balance.get_balance_seconds()
    
    def _schedule_next_tick(self) -> None:
        """Schedule the next timer tick."""
        if self._state == TimerState.RUNNING:
            self._timer = threading.Timer(1.0, self._tick)
            self._timer.start()
    
    def _cancel_timer(self) -> None:
        """Cancel the current timer."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
    
    def _tick(self) -> None:
        """Internal timer tick method that consumes time balance."""
        # Only consume time if we're in running state
        if self._state != TimerState.RUNNING:
            return
        
        # Only tick if we have a time balance
        if self._time_balance is None:
            self.stop()
            return
        
        # Try to consume 1 second
        success = self._time_balance.subtract_time(1)
        
        if not success or self._time_balance.get_balance_seconds() <= 0:
            # No more time available, stop the timer
            self.stop()
            if self._tick_callback:
                self._tick_callback(0)
        else:
            # Call callback with remaining time
            if self._tick_callback:
                self._tick_callback(self._time_balance.get_balance_seconds())
            
            # Schedule next tick if still running
            if self._state == TimerState.RUNNING:
                self._schedule_next_tick() 