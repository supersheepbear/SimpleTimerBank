"""Countdown timer management module.

This module will contain the CountdownTimer class responsible for managing
the countdown timer functionality that consumes time balance.
Full implementation will be done in Phase 2 - Task 2.2.
"""

from enum import Enum
from typing import Callable, Optional


class TimerState(Enum):
    """Enumeration of possible timer states."""
    STOPPED = "stopped"
    RUNNING = "running" 
    PAUSED = "paused"


class CountdownTimer:
    """Manages countdown timer operations for the SimpleTimerBank application.
    
    This class handles starting, pausing, stopping the countdown timer
    and coordinating with the TimeBalance to consume time.
    
    Note
    ----
    This is a placeholder stub. Full implementation in Phase 2 - Task 2.2.
    """
    
    def __init__(self, time_balance: Optional[object] = None) -> None:
        """Initialize CountdownTimer.
        
        Parameters
        ----------
        time_balance : TimeBalance, optional
            Reference to the time balance manager.
        """
        # TODO: Implement in Phase 2 - Task 2.2
        pass
    
    def start(self) -> bool:
        """Start the countdown timer.
        
        Returns
        -------
        bool
            True if timer started successfully, False if insufficient balance.
        """
        # TODO: Implement in Phase 2 - Task 2.2
        return False
    
    def pause(self) -> None:
        """Pause the countdown timer."""
        # TODO: Implement in Phase 2 - Task 2.2
        pass
    
    def stop(self) -> None:
        """Stop the countdown timer and reset."""
        # TODO: Implement in Phase 2 - Task 2.2
        pass
    
    def get_state(self) -> TimerState:
        """Get current timer state.
        
        Returns
        -------
        TimerState
            Current state of the timer.
        """
        # TODO: Implement in Phase 2 - Task 2.2
        return TimerState.STOPPED
    
    def set_tick_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback function to be called every timer tick.
        
        Parameters
        ----------
        callback : Callable[[int], None]
            Function to call with remaining seconds on each tick.
        """
        # TODO: Implement in Phase 2 - Task 2.2
        pass 