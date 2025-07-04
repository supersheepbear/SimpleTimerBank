"""Unit tests for CountdownTimer class.

This module contains comprehensive unit tests for the CountdownTimer class,
following the pytest protocol with pure unit testing and mocked time operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from simpletimerbank.core.countdown_timer import CountdownTimer, TimerState
from simpletimerbank.core.time_balance import TimeBalance


class TestCountdownTimer:
    """Test suite for CountdownTimer class."""
    
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
    
    def test_pause_running_timer(self) -> None:
        """Test pausing a running timer."""
        tb = TimeBalance()
        tb.add_time(300)
        timer = CountdownTimer(tb)
        
        timer.start()
        timer.pause()
        assert timer.get_state() == TimerState.PAUSED
    
    def test_pause_stopped_timer_does_nothing(self) -> None:
        """Test pausing a stopped timer does nothing."""
        timer = CountdownTimer()
        timer.pause()
        assert timer.get_state() == TimerState.STOPPED
    
    def test_pause_already_paused_timer_does_nothing(self) -> None:
        """Test pausing already paused timer does nothing."""
        tb = TimeBalance()
        tb.add_time(300)
        timer = CountdownTimer(tb)
        
        timer.start()
        timer.pause()
        timer.pause()  # Pause again
        assert timer.get_state() == TimerState.PAUSED
    
    def test_stop_running_timer(self) -> None:
        """Test stopping a running timer."""
        tb = TimeBalance()
        tb.add_time(300)
        timer = CountdownTimer(tb)
        
        timer.start()
        timer.stop()
        assert timer.get_state() == TimerState.STOPPED
    
    def test_stop_paused_timer(self) -> None:
        """Test stopping a paused timer."""
        tb = TimeBalance()
        tb.add_time(300)
        timer = CountdownTimer(tb)
        
        timer.start()
        timer.pause()
        timer.stop()
        assert timer.get_state() == TimerState.STOPPED
    
    def test_stop_already_stopped_timer_does_nothing(self) -> None:
        """Test stopping already stopped timer does nothing."""
        timer = CountdownTimer()
        timer.stop()
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