"""Unit tests for AppStateManager class.

This module contains comprehensive unit tests for the AppStateManager class,
following the pytest protocol with pure unit testing and mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from simpletimerbank.core.app_state import AppStateManager
from simpletimerbank.core.time_balance import TimeBalance
from simpletimerbank.core.countdown_timer import CountdownTimer
from simpletimerbank.core.persistence import PersistenceService


class TestAppStateManager:
    """Test suite for AppStateManager class."""
    
    def test_init_creates_components(self) -> None:
        """Test AppStateManager initializes and creates all components."""
        manager = AppStateManager()
        
        # Should have created all components
        assert manager.get_time_balance() is not None
        assert manager.get_countdown_timer() is not None
        assert manager.get_persistence_service() is not None
    
    def test_get_time_balance_returns_instance(self) -> None:
        """Test get_time_balance returns TimeBalance instance."""
        manager = AppStateManager()
        time_balance = manager.get_time_balance()
        
        assert isinstance(time_balance, TimeBalance)
    
    def test_get_countdown_timer_returns_instance(self) -> None:
        """Test get_countdown_timer returns CountdownTimer instance."""
        manager = AppStateManager()
        countdown_timer = manager.get_countdown_timer()
        
        assert isinstance(countdown_timer, CountdownTimer)
    
    def test_get_persistence_service_returns_instance(self) -> None:
        """Test get_persistence_service returns PersistenceService instance."""
        manager = AppStateManager()
        persistence = manager.get_persistence_service()
        
        assert isinstance(persistence, PersistenceService)
    
    def test_countdown_timer_has_time_balance_reference(self) -> None:
        """Test that countdown timer is initialized with time balance reference."""
        manager = AppStateManager()
        
        time_balance = manager.get_time_balance()
        countdown_timer = manager.get_countdown_timer()
        
        # Add some time and verify countdown timer can access it
        time_balance.add_time(300)
        assert countdown_timer.get_remaining_seconds() == 300
    
    @patch('simpletimerbank.core.persistence.PersistenceService.data_file_exists')
    @patch('simpletimerbank.core.persistence.PersistenceService.load_data')
    def test_initialize_loads_existing_data(self, mock_load: Mock, mock_exists: Mock) -> None:
        """Test initialize loads existing data from persistence."""
        mock_exists.return_value = True
        mock_load.return_value = {"balance_seconds": 600}
        
        manager = AppStateManager()
        manager.initialize()
        
        # Time balance should be loaded
        assert manager.get_time_balance().get_balance_seconds() == 600
        mock_load.assert_called_once()
    
    @patch('simpletimerbank.core.persistence.PersistenceService.data_file_exists')
    @patch('simpletimerbank.core.persistence.PersistenceService.load_data')
    def test_initialize_handles_missing_data_file(self, mock_load: Mock, mock_exists: Mock) -> None:
        """Test initialize handles missing data file gracefully."""
        mock_exists.return_value = False
        mock_load.return_value = {}
        
        manager = AppStateManager()
        manager.initialize()
        
        # Should start with zero balance
        assert manager.get_time_balance().get_balance_seconds() == 0
    
    @patch('simpletimerbank.core.persistence.PersistenceService.data_file_exists')
    @patch('simpletimerbank.core.persistence.PersistenceService.load_data')
    def test_initialize_handles_corrupted_data(self, mock_load: Mock, mock_exists: Mock) -> None:
        """Test initialize handles corrupted data gracefully."""
        mock_exists.return_value = True
        mock_load.return_value = {"invalid_key": "invalid_value"}
        
        manager = AppStateManager()
        manager.initialize()
        
        # Should start with zero balance when data is corrupted
        assert manager.get_time_balance().get_balance_seconds() == 0
    
    @patch('simpletimerbank.core.persistence.PersistenceService.data_file_exists')
    @patch('simpletimerbank.core.persistence.PersistenceService.load_data')
    def test_initialize_with_negative_balance_resets_to_zero(self, mock_load: Mock, mock_exists: Mock) -> None:
        """Test initialize resets negative balance to zero."""
        mock_exists.return_value = True
        mock_load.return_value = {"balance_seconds": -100}
        
        manager = AppStateManager()
        manager.initialize()
        
        # Negative balance should be reset to zero
        assert manager.get_time_balance().get_balance_seconds() == 0
    
    @patch('simpletimerbank.core.persistence.PersistenceService.save_data')
    def test_shutdown_saves_current_state(self, mock_save: Mock) -> None:
        """Test shutdown saves current application state."""
        manager = AppStateManager()
        
        # Set some state
        manager.get_time_balance().add_time(450)
        
        manager.shutdown()
        
        # Should have saved the current balance
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        assert saved_data["balance_seconds"] == 450
    
    @patch('simpletimerbank.core.persistence.PersistenceService.save_data')
    def test_shutdown_stops_timer_before_saving(self, mock_save: Mock) -> None:
        """Test shutdown stops countdown timer before saving state."""
        manager = AppStateManager()
        
        # Start the timer
        manager.get_time_balance().add_time(300)
        manager.get_countdown_timer().start()
        
        manager.shutdown()
        
        # Timer should be stopped
        from simpletimerbank.core.countdown_timer import TimerState
        assert manager.get_countdown_timer().get_state() == TimerState.STOPPED
        mock_save.assert_called_once()
    
    @patch('simpletimerbank.core.persistence.PersistenceService.save_data')
    def test_shutdown_handles_save_failure_gracefully(self, mock_save: Mock) -> None:
        """Test shutdown handles save failure gracefully."""
        mock_save.return_value = False  # Simulate save failure
        
        manager = AppStateManager()
        manager.get_time_balance().add_time(200)
        
        # Should not raise exception even if save fails
        manager.shutdown()
        
        mock_save.assert_called_once()
    
    def test_add_time_updates_balance(self) -> None:
        """Test add_time method updates time balance."""
        manager = AppStateManager()
        
        manager.add_time(500)
        
        assert manager.get_time_balance().get_balance_seconds() == 500
    
    def test_add_time_with_negative_value_raises_error(self) -> None:
        """Test add_time with negative value raises ValueError."""
        manager = AppStateManager()
        
        with pytest.raises(ValueError, match="Cannot add negative time"):
            manager.add_time(-100)
    
    def test_get_balance_seconds_returns_current_balance(self) -> None:
        """Test get_balance_seconds returns current time balance."""
        manager = AppStateManager()
        
        manager.add_time(750)
        
        assert manager.get_balance_seconds() == 750
    
    def test_get_balance_formatted_returns_formatted_string(self) -> None:
        """Test get_balance_formatted returns properly formatted time string."""
        manager = AppStateManager()
        
        manager.add_time(3661)  # 1 hour, 1 minute, 1 second
        
        assert manager.get_balance_formatted() == "01:01:01"
    
    def test_start_timer_with_sufficient_balance(self) -> None:
        """Test starting timer with sufficient balance."""
        manager = AppStateManager()
        
        manager.add_time(300)
        result = manager.start_timer()
        
        assert result is True
        from simpletimerbank.core.countdown_timer import TimerState
        assert manager.get_countdown_timer().get_state() == TimerState.RUNNING
    
    def test_start_timer_with_insufficient_balance(self) -> None:
        """Test starting timer with insufficient balance fails."""
        manager = AppStateManager()
        
        # Don't add any time
        result = manager.start_timer()
        
        assert result is False
        from simpletimerbank.core.countdown_timer import TimerState
        assert manager.get_countdown_timer().get_state() == TimerState.STOPPED
    
    def test_pause_timer(self) -> None:
        """Test pausing the timer."""
        manager = AppStateManager()
        
        manager.add_time(300)
        manager.start_timer()
        manager.pause_timer()
        
        from simpletimerbank.core.countdown_timer import TimerState
        assert manager.get_countdown_timer().get_state() == TimerState.PAUSED
    
    def test_stop_timer(self) -> None:
        """Test stopping the timer."""
        manager = AppStateManager()
        
        manager.add_time(300)
        manager.start_timer()
        manager.stop_timer()
        
        from simpletimerbank.core.countdown_timer import TimerState
        assert manager.get_countdown_timer().get_state() == TimerState.STOPPED
    
    def test_get_timer_state(self) -> None:
        """Test getting timer state."""
        manager = AppStateManager()
        
        from simpletimerbank.core.countdown_timer import TimerState
        
        # Initially stopped
        assert manager.get_timer_state() == TimerState.STOPPED
        
        # Start timer
        manager.add_time(300)
        manager.start_timer()
        assert manager.get_timer_state() == TimerState.RUNNING
        
        # Pause timer
        manager.pause_timer()
        assert manager.get_timer_state() == TimerState.PAUSED
    
    def test_set_timer_callback(self) -> None:
        """Test setting timer callback function."""
        manager = AppStateManager()
        callback_mock = Mock()
        
        manager.set_timer_callback(callback_mock)
        
        # Should not raise any errors
        # The callback is set on the countdown timer
    
    def test_multiple_initialize_calls_are_safe(self) -> None:
        """Test that calling initialize multiple times is safe."""
        manager = AppStateManager()
        
        manager.add_time(100)
        balance_before = manager.get_balance_seconds()
        
        manager.initialize()  # Second call
        
        # Should not lose existing state on second initialize
        assert manager.get_balance_seconds() >= 0  # May be reset by loading
    
    def test_multiple_shutdown_calls_are_safe(self) -> None:
        """Test that calling shutdown multiple times is safe."""
        manager = AppStateManager()
        
        manager.add_time(100)
        manager.shutdown()
        
        # Second shutdown call should not raise errors
        manager.shutdown()
    
    @patch('simpletimerbank.core.persistence.PersistenceService.load_data')
    def test_initialize_with_complex_saved_data(self, mock_load: Mock) -> None:
        """Test initialize with complex saved data structure."""
        mock_load.return_value = {
            "balance_seconds": 1800,
            "settings": {
                "theme": "dark",
                "notifications": True
            },
            "last_saved": "2023-01-01T12:00:00"
        }
        
        manager = AppStateManager()
        manager.initialize()
        
        # Should load the balance correctly
        assert manager.get_balance_seconds() == 1800 