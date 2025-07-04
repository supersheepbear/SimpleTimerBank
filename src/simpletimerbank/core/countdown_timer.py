"""Countdown timer management module.

This module contains the CountdownTimer class responsible for managing
the countdown timer functionality with support for overdraft mode.
"""

from enum import Enum
from typing import Callable, Optional, Union


class TimerState(Enum):
    """Enumeration of possible timer states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class CountdownTimer:
    """Manages countdown timer operations for the SimpleTimerBank application.
    
    This class handles starting, pausing, resuming, and stopping the countdown timer.
    It also supports an overdraft mode that is triggered when the timer reaches zero
    and continues running.
    """
    
    def __init__(self) -> None:
        """Initialize CountdownTimer in IDLE state."""
        self._state: TimerState = TimerState.IDLE
        self._remaining_seconds: int = 0
        self._initial_duration: int = 0
        self._is_overdrafting: bool = False
        self._tick_callback: Optional[Callable[[int], None]] = None
        self._completion_callback: Optional[Callable[[], None]] = None
    
    def start(self, duration: int) -> None:
        """Start the countdown timer with the specified duration.
        
        Parameters
        ----------
        duration : int
            The duration in seconds for the timer.
            
        Raises
        ------
        ValueError
            If duration is not positive or timer is already running.
        """
        if duration <= 0:
            raise ValueError("Duration must be positive")
            
        if self._state == TimerState.RUNNING:
            raise ValueError("Timer is already running")
        
        self._initial_duration = duration
        self._remaining_seconds = duration
        self._is_overdrafting = False
        self._state = TimerState.RUNNING
    
    def pause(self) -> None:
        """Pause the countdown timer.
        
        Raises
        ------
        ValueError
            If timer is not in RUNNING state.
        """
        if self._state != TimerState.RUNNING:
            if self._state == TimerState.PAUSED:
                raise ValueError("Timer is already paused")
            else:
                raise ValueError("Timer is not running")
        
        self._state = TimerState.PAUSED
    
    def resume(self) -> None:
        """Resume a paused countdown timer.
        
        Raises
        ------
        ValueError
            If timer is not in PAUSED state.
        """
        if self._state != TimerState.PAUSED:
            raise ValueError("Timer is not paused")
        
        self._state = TimerState.RUNNING
    
    def stop(self) -> None:
        """Stop the countdown timer.
        
        When stopped, the timer preserves its remaining seconds for refund
        purposes, unless it's in overdraft mode.
        
        Raises
        ------
        ValueError
            If timer has not been started or is already stopped.
        """
        if self._state == TimerState.IDLE:
            raise ValueError("Timer has not been started")
            
        if self._state == TimerState.STOPPED:
            raise ValueError("Timer is already stopped")
        
        self._state = TimerState.STOPPED
        
        # If in overdraft, set remaining seconds to 0 (no refund)
        if self._is_overdrafting:
            self._remaining_seconds = 0
            self._is_overdrafting = False
    
    def tick(self) -> Optional[int]:
        """Process a timer tick.
        
        This method should be called every second when the timer is running.
        It decrements the remaining seconds and handles the transition to
        overdraft mode when the timer reaches zero.
        
        Returns
        -------
        Optional[int]
            None if not in overdraft mode, or the number of seconds (1) to
            withdraw from the bank if in overdraft mode.
        """
        if self._state != TimerState.RUNNING:
            return None
        
        # If already in overdraft mode, signal to withdraw 1 second
        if self._is_overdrafting:
            if self._tick_callback:
                self._tick_callback(0)
            return 1
            
        # Normal countdown mode - decrement time
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            
            # Call tick callback with new remaining time
            if self._tick_callback:
                self._tick_callback(self._remaining_seconds)
            
            # Check if we've just reached zero
            if self._remaining_seconds == 0:
                self._is_overdrafting = True
                # Notify that the initial countdown is complete
                if self._completion_callback:
                    self._completion_callback()
            
            return None
            
        return None
    
    def get_state(self) -> TimerState:
        """Get current timer state.
        
        Returns
        -------
        TimerState
            Current state of the timer.
        """
        return self._state
    
    def get_remaining_seconds(self) -> int:
        """Get remaining time in seconds.
        
        Returns
        -------
        int
            Remaining time in seconds.
        """
        return self._remaining_seconds
    
    def is_overdrafting(self) -> bool:
        """Check if the timer is in overdraft mode.
        
        Returns
        -------
        bool
            True if the timer is in overdraft mode, False otherwise.
        """
        return self._is_overdrafting
    
    def set_tick_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback function to be called every timer tick.
        
        Parameters
        ----------
        callback : Callable[[int], None]
            Function to call with remaining seconds on each tick.
        """
        self._tick_callback = callback
    
    def set_completion_callback(self, callback: Callable[[], None]) -> None:
        """Set callback function to be called when timer completes.
        
        This callback is called when the timer transitions from normal
        countdown to overdraft mode.
        
        Parameters
        ----------
        callback : Callable[[], None]
            Function to call when timer completes.
        """
        self._completion_callback = callback 