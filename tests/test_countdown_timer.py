"""Unit tests for CountdownTimer class.

This module contains comprehensive unit tests for the CountdownTimer class,
following the pytest protocol with pure unit testing and mocked time operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from simpletimerbank.core.countdown_timer import CountdownTimer, TimerState
from simpletimerbank.core.time_balance import TimeBalance


class TestCountdownTimer:
    """Test suite for CountdownTimer class."""
    
    def test_init_state(self) -> None:
        """Test that CountdownTimer initializes in IDLE state."""
        timer = CountdownTimer()
        assert timer.get_state() == TimerState.IDLE
        assert not timer.is_overdrafting()
        assert timer.get_remaining_seconds() == 0
    
    def test_start_with_valid_duration(self) -> None:
        """Test starting timer with a valid duration."""
        timer = CountdownTimer()
        timer.start(60)
        assert timer.get_state() == TimerState.RUNNING
        assert timer.get_remaining_seconds() == 60
        assert not timer.is_overdrafting()
    
    def test_start_with_zero_duration_fails(self) -> None:
        """Test starting timer with zero duration fails."""
        timer = CountdownTimer()
        with pytest.raises(ValueError, match="Duration must be positive"):
            timer.start(0)
        assert timer.get_state() == TimerState.IDLE
    
    def test_start_with_negative_duration_fails(self) -> None:
        """Test starting timer with negative duration fails."""
        timer = CountdownTimer()
        with pytest.raises(ValueError, match="Duration must be positive"):
            timer.start(-1)
        assert timer.get_state() == TimerState.IDLE
    
    def test_start_when_already_running_fails(self) -> None:
        """Test starting an already running timer fails."""
        timer = CountdownTimer()
        timer.start(60)
        with pytest.raises(ValueError, match="Timer is already running"):
            timer.start(30)
        assert timer.get_state() == TimerState.RUNNING
        assert timer.get_remaining_seconds() == 60  # Original duration remains
    
    def test_pause_running_timer(self) -> None:
        """Test pausing a running timer."""
        timer = CountdownTimer()
        timer.start(60)
        timer.pause()
        assert timer.get_state() == TimerState.PAUSED
        assert timer.get_remaining_seconds() == 60  # Duration shouldn't change
    
    def test_pause_idle_timer_fails(self) -> None:
        """Test pausing an idle timer fails."""
        timer = CountdownTimer()
        with pytest.raises(ValueError, match="Timer is not running"):
            timer.pause()
        assert timer.get_state() == TimerState.IDLE
    
    def test_pause_already_paused_timer_fails(self) -> None:
        """Test pausing an already paused timer fails."""
        timer = CountdownTimer()
        timer.start(60)
        timer.pause()
        with pytest.raises(ValueError, match="Timer is already paused"):
            timer.pause()
        assert timer.get_state() == TimerState.PAUSED
    
    def test_resume_paused_timer(self) -> None:
        """Test resuming a paused timer."""
        timer = CountdownTimer()
        timer.start(60)
        timer.pause()
        timer.resume()
        assert timer.get_state() == TimerState.RUNNING
        assert timer.get_remaining_seconds() == 60
    
    def test_resume_non_paused_timer_fails(self) -> None:
        """Test resuming a timer that's not paused fails."""
        timer = CountdownTimer()
        with pytest.raises(ValueError, match="Timer is not paused"):
            timer.resume()
        
        # Also test when running
        timer.start(60)
        with pytest.raises(ValueError, match="Timer is not paused"):
            timer.resume()
    
    def test_stop_running_timer(self) -> None:
        """Test stopping a running timer."""
        timer = CountdownTimer()
        timer.start(60)
        timer.stop()
        assert timer.get_state() == TimerState.STOPPED
        assert timer.get_remaining_seconds() == 60  # Duration preserved for refund
    
    def test_stop_paused_timer(self) -> None:
        """Test stopping a paused timer."""
        timer = CountdownTimer()
        timer.start(60)
        timer.pause()
        timer.stop()
        assert timer.get_state() == TimerState.STOPPED
        assert timer.get_remaining_seconds() == 60  # Duration preserved for refund
    
    def test_stop_idle_timer_fails(self) -> None:
        """Test stopping an idle timer fails."""
        timer = CountdownTimer()
        with pytest.raises(ValueError, match="Timer has not been started"):
            timer.stop()
        assert timer.get_state() == TimerState.IDLE
    
    def test_stop_already_stopped_timer_fails(self) -> None:
        """Test stopping an already stopped timer fails."""
        timer = CountdownTimer()
        timer.start(60)
        timer.stop()
        with pytest.raises(ValueError, match="Timer is already stopped"):
            timer.stop()
        assert timer.get_state() == TimerState.STOPPED
    
    def test_tick_decrements_remaining_seconds(self) -> None:
        """Test that tick decrements remaining seconds when running."""
        timer = CountdownTimer()
        timer.start(60)
        
        # Execute a tick
        result = timer.tick()
        
        assert timer.get_remaining_seconds() == 59
        assert result is None  # No overdraft signal
        assert not timer.is_overdrafting()
    
    def test_tick_in_non_running_state_does_nothing(self) -> None:
        """Test that tick doesn't change remaining seconds when not running."""
        timer = CountdownTimer()
        timer.start(60)
        timer.pause()
        
        # Should not change in PAUSED state
        timer.tick()
        assert timer.get_remaining_seconds() == 60
        
        # Should not change in STOPPED state
        timer.resume()
        timer.stop()
        timer.tick()
        assert timer.get_remaining_seconds() == 60
        
        # Should do nothing in IDLE state
        timer = CountdownTimer()
        timer.tick()
        assert timer.get_remaining_seconds() == 0
    
    def test_tick_to_zero_enters_overdraft(self) -> None:
        """Test that tick enters overdraft mode when seconds reach zero."""
        timer = CountdownTimer()
        timer.start(1)  # Start with just 1 second
        
        # This tick should consume the last second and enter overdraft
        result = timer.tick()
        
        assert timer.get_remaining_seconds() == 0
        assert timer.is_overdrafting()
        assert timer.get_state() == TimerState.RUNNING
        assert result is None  # Still no signal on the transition tick
    
    def test_tick_in_overdraft_returns_overdraft_signal(self) -> None:
        """Test that tick in overdraft mode returns a signal."""
        timer = CountdownTimer()
        timer.start(1)
        timer.tick()  # Enters overdraft
        
        # Next tick should signal overdraft
        result = timer.tick()
        
        assert result == 1  # Signal 1 second of overdraft
        assert timer.is_overdrafting()
        assert timer.get_state() == TimerState.RUNNING
        
        # Another tick should continue to signal
        result = timer.tick()
        assert result == 1
    
    def test_stop_in_overdraft_resets_overdraft_flag(self) -> None:
        """Test that stopping in overdraft resets the overdraft flag."""
        timer = CountdownTimer()
        timer.start(1)
        timer.tick()  # Enters overdraft
        timer.tick()  # One tick in overdraft
        
        timer.stop()
        
        assert not timer.is_overdrafting()
        assert timer.get_state() == TimerState.STOPPED
        assert timer.get_remaining_seconds() == 0  # No refund in overdraft
    
    def test_tick_callback_called_with_remaining_seconds(self) -> None:
        """Test that tick callback is called with the correct remaining seconds."""
        timer = CountdownTimer()
        callback_mock = Mock()
        timer.set_tick_callback(callback_mock)
        
        timer.start(60)
        timer.tick()
        
        callback_mock.assert_called_once_with(59)
    
    def test_tick_callback_called_with_zero_in_overdraft(self) -> None:
        """Test that tick callback shows zero seconds in overdraft mode."""
        timer = CountdownTimer()
        callback_mock = Mock()
        timer.set_tick_callback(callback_mock)
        
        timer.start(1)
        timer.tick()  # Enters overdraft with 0 seconds
        callback_mock.reset_mock()
        
        timer.tick()  # First overdraft tick
        callback_mock.assert_called_once_with(0)
    
    def test_overdraft_completion_callback(self) -> None:
        """Test that completion callback is called when entering overdraft."""
        timer = CountdownTimer()
        completion_callback = Mock()
        timer.set_completion_callback(completion_callback)
        
        timer.start(1)
        timer.tick()  # This should trigger the completion callback
        
        completion_callback.assert_called_once()
    
    def test_multiple_session_resets_state(self) -> None:
        """Test that a new start after stop resets the timer state correctly."""
        timer = CountdownTimer()
        
        # First session with overdraft
        timer.start(1)
        timer.tick()  # Goes to 0, enters overdraft
        timer.tick()  # One overdraft tick
        timer.stop()
        
        # Second session should start fresh
        timer.start(30)
        assert timer.get_state() == TimerState.RUNNING
        assert timer.get_remaining_seconds() == 30
        assert not timer.is_overdrafting()
    
    def test_comprehensive_timer_lifecycle(self) -> None:
        """Test a comprehensive timer lifecycle including all state transitions."""
        callback_mock = Mock()
        completion_mock = Mock()
        
        timer = CountdownTimer()
        timer.set_tick_callback(callback_mock)
        timer.set_completion_callback(completion_mock)
        
        # Start with 2 seconds
        timer.start(2)
        assert timer.get_state() == TimerState.RUNNING
        assert timer.get_remaining_seconds() == 2
        
        # First tick
        timer.tick()
        assert timer.get_remaining_seconds() == 1
        callback_mock.assert_called_with(1)
        completion_mock.assert_not_called()
        
        # Pause
        timer.pause()
        assert timer.get_state() == TimerState.PAUSED
        
        # Resume
        timer.resume()
        assert timer.get_state() == TimerState.RUNNING
        
        # Second tick - should enter overdraft
        callback_mock.reset_mock()
        timer.tick()
        assert timer.get_remaining_seconds() == 0
        assert timer.is_overdrafting()
        callback_mock.assert_called_with(0)
        completion_mock.assert_called_once()
        
        # Overdraft tick
        callback_mock.reset_mock()
        completion_mock.reset_mock()
        result = timer.tick()
        assert result == 1  # Overdraft signal
        callback_mock.assert_called_with(0)
        completion_mock.assert_not_called()  # Called only once at completion
        
        # Stop and verify state
        timer.stop()
        assert timer.get_state() == TimerState.STOPPED
        assert not timer.is_overdrafting()
    
    def test_init_with_time_balance(self) -> None:
        """Test CountdownTimer initializes correctly with TimeBalance."""
        tb = TimeBalance()
        timer = CountdownTimer(tb)
        assert timer.get_state() == TimerState.STOPPED
    
    def test_init_without_time_balance(self) -> None:
        """Test CountdownTimer initializes correctly without TimeBalance."""
        timer = CountdownTimer()
        assert timer.get_state() == TimerState.STOPPED
    
    def test_start_with_sufficient_balance_succeeds(self) -> None:
        """Test starting timer with sufficient balance succeeds."""
        tb = TimeBalance()
        tb.add_time(300)  # 5 minutes
        timer = CountdownTimer(tb)
        
        result = timer.start()
        assert result is True
        assert timer.get_state() == TimerState.RUNNING
    
    def test_start_with_insufficient_balance_fails(self) -> None:
        """Test starting timer with insufficient balance fails."""
        tb = TimeBalance()
        # Don't add any time - balance is 0
        timer = CountdownTimer(tb)
        
        result = timer.start()
        assert result is False
        assert timer.get_state() == TimerState.STOPPED
    
    def test_start_without_time_balance_fails(self) -> None:
        """Test starting timer without TimeBalance fails."""
        timer = CountdownTimer()
        
        result = timer.start()
        assert result is False
        assert timer.get_state() == TimerState.STOPPED
    
    def test_start_already_running_timer_returns_false(self) -> None:
        """Test starting already running timer returns False."""
        tb = TimeBalance()
        tb.add_time(300)
        timer = CountdownTimer(tb)
        
        # Start once
        result1 = timer.start()
        assert result1 is True
        
        # Try to start again
        result2 = timer.start()
        assert result2 is False
        assert timer.get_state() == TimerState.RUNNING
    
    def test_pause_stopped_timer_does_nothing(self) -> None:
        """Test pausing a stopped timer does nothing."""
        timer = CountdownTimer()
        timer.pause()
        assert timer.get_state() == TimerState.STOPPED
    
    def test_resume_paused_timer(self) -> None:
        """Test resuming a paused timer."""
        tb = TimeBalance()
        tb.add_time(300)
        timer = CountdownTimer(tb)
        
        timer.start()
        timer.pause()
        result = timer.start()  # Should resume
        assert result is True
        assert timer.get_state() == TimerState.RUNNING
    
    def test_set_tick_callback(self) -> None:
        """Test setting tick callback function."""
        timer = CountdownTimer()
        callback_mock = Mock()
        
        timer.set_tick_callback(callback_mock)
        # Should not raise any errors
    
    @patch('threading.Timer')
    def test_timer_tick_consumes_balance(self, mock_timer_class: Mock) -> None:
        """Test that timer tick consumes balance correctly."""
        # Mock the Timer class
        mock_timer_instance = MagicMock()
        mock_timer_class.return_value = mock_timer_instance
        
        tb = TimeBalance()
        tb.add_time(10)  # 10 seconds
        timer = CountdownTimer(tb)
        
        callback_mock = Mock()
        timer.set_tick_callback(callback_mock)
        
        # Start timer
        timer.start()
        
        # Simulate timer ticks by calling the internal tick method directly
        # This tests the core logic without relying on actual threading
        initial_balance = tb.get_balance_seconds()
        
        # Simulate a tick
        timer._tick()
        
        # Balance should be reduced by 1 second
        assert tb.get_balance_seconds() == initial_balance - 1
        
        # Callback should be called with remaining time
        callback_mock.assert_called_with(tb.get_balance_seconds())
    
    @patch('threading.Timer')
    def test_timer_stops_when_balance_reaches_zero(self, mock_timer_class: Mock) -> None:
        """Test that timer stops automatically when balance reaches zero."""
        mock_timer_instance = MagicMock()
        mock_timer_class.return_value = mock_timer_instance
        
        tb = TimeBalance()
        tb.add_time(1)  # Only 1 second
        timer = CountdownTimer(tb)
        
        callback_mock = Mock()
        timer.set_tick_callback(callback_mock)
        
        timer.start()
        
        # Simulate the final tick that consumes the last second
        timer._tick()
        
        # Timer should be stopped
        assert timer.get_state() == TimerState.STOPPED
        assert tb.get_balance_seconds() == 0
    
    @patch('threading.Timer')
    def test_timer_paused_does_not_consume_balance(self, mock_timer_class: Mock) -> None:
        """Test that paused timer does not consume balance."""
        mock_timer_instance = MagicMock()
        mock_timer_class.return_value = mock_timer_instance
        
        tb = TimeBalance()
        tb.add_time(300)
        timer = CountdownTimer(tb)
        
        timer.start()
        initial_balance = tb.get_balance_seconds()
        
        timer.pause()
        
        # Try to tick while paused - should not consume balance
        timer._tick()
        
        assert tb.get_balance_seconds() == initial_balance
        assert timer.get_state() == TimerState.PAUSED
    
    def test_get_remaining_time_with_balance(self) -> None:
        """Test getting remaining time when timer has balance."""
        tb = TimeBalance()
        tb.add_time(150)
        timer = CountdownTimer(tb)
        
        assert timer.get_remaining_seconds() == 150
    
    def test_get_remaining_time_without_balance(self) -> None:
        """Test getting remaining time when timer has no balance."""
        timer = CountdownTimer()
        
        assert timer.get_remaining_seconds() == 0
    
    def test_multiple_start_stop_cycles(self) -> None:
        """Test multiple start/stop cycles work correctly."""
        tb = TimeBalance()
        tb.add_time(1000)
        timer = CountdownTimer(tb)
        
        # First cycle
        assert timer.start() is True
        assert timer.get_state() == TimerState.RUNNING
        timer.stop()
        assert timer.get_state() == TimerState.STOPPED
        
        # Second cycle
        assert timer.start() is True
        assert timer.get_state() == TimerState.RUNNING
        timer.pause()
        assert timer.get_state() == TimerState.PAUSED
        timer.stop()
        assert timer.get_state() == TimerState.STOPPED 