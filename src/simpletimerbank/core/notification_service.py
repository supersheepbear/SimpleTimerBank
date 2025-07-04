"""Notification service module.

This module provides a service for sending desktop notifications to the user.
"""

from plyer import notification


class NotificationService:
    """Service for sending desktop notifications.
    
    This class provides methods for sending various types of notifications
    related to the timer and bank state.
    """
    
    def __init__(self) -> None:
        """Initialize the NotificationService."""
        self._app_name = "SimpleTimerBank"
    
    def notify_timer_completed(self) -> None:
        """Send a notification that the timer has completed its initial countdown.
        
        This notification is sent when the timer reaches zero and transitions
        to overdraft mode.
        """
        notification.notify(
            title=f"{self._app_name} - Timer Completed",
            message="Your timer has completed its initial countdown and is now withdrawing from your bank balance.",
            app_name=self._app_name,
            timeout=10
        )
    
    def notify_overdraft_started(self) -> None:
        """Send a notification that overdraft mode has started.
        
        This is similar to notify_timer_completed but with a focus on
        the fact that the bank is now being depleted.
        """
        notification.notify(
            title=f"{self._app_name} - Overdraft Mode Started",
            message="Your timer is now withdrawing time from your bank balance. Stop the timer to prevent further depletion.",
            app_name=self._app_name,
            timeout=10
        )
    
    def notify_bank_depleted(self) -> None:
        """Send a notification that the bank balance has been depleted.
        
        This notification is sent when the timer is in overdraft mode and
        the bank balance reaches zero.
        """
        notification.notify(
            title=f"{self._app_name} - Bank Balance Depleted",
            message="Your bank balance has been depleted. The timer has been stopped.",
            app_name=self._app_name,
            timeout=10
        ) 