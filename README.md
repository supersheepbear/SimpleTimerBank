# SimpleTimerBank

A desktop application that allows you to store units of time in a "bank" and spend them via a countdown timer.

## Features

- **Time Bank**: Store time units (hours, minutes, seconds) that you can later withdraw for focused work sessions.
- **Balance Management**: Add or subtract time from your bank balance manually.
- **Timer Controls**: Start, pause, and stop a timer session funded by your bank balance.
- **Refund System**: When you stop a timer early, unused time is automatically refunded to your bank.
- **Overdraft Mode**: If a timer completes its countdown and is not stopped, it enters overdraft mode and withdraws time from your bank balance.
- **Desktop Notifications**: Receive notifications when important events occur, such as timer completion or bank depletion.
- **Visual Indicators**: Clear visual cues show when you're in overdraft mode, including color changes and status messages.

## Requirements

- Python 3.8 or higher
- PySide6 (Qt for Python)
- Plyer (for cross-platform notifications)

## Installation

1. Clone this repository
2. Install the package in development mode:

```
uv add -e .
```

## Usage

### Running the Application

On Windows, you can run the application using the provided batch file:

```
run_app.cmd
```

Alternatively, you can run it directly using Python:

```
uv run python -m simpletimerbank.main
```

### Using the Application

1. **Adding Time to Your Bank**:
   - Use the "Add" button to add time to your bank balance.
   - Enter the amount of time (hours, minutes, seconds) you want to add.

2. **Starting a Timer Session**:
   - The current bank balance will be used as the timer duration.
   - Click "Start" to begin the timer countdown.

3. **Controlling the Timer**:
   - Use "Pause" to temporarily pause the timer.
   - Use "Stop" to end the timer session early and refund unused time to your bank.

4. **Overdraft Mode**:
   - If the timer reaches zero and is not stopped, it enters overdraft mode.
   - In this mode, the timer will withdraw time from your bank balance.
   - The display will turn red to indicate overdraft mode.
   - You'll receive a desktop notification when entering overdraft mode.

5. **Bank Depletion**:
   - If your bank balance reaches zero during overdraft, the timer will stop automatically.
   - You'll receive a notification when your bank is depleted.

## Development

### Running Tests

```
make test
```

### Project Structure

- `src/simpletimerbank/`: Main package directory
  - `core/`: Core business logic
    - `time_bank.py`: Manages the time balance
    - `countdown_timer.py`: Handles timer functionality
    - `app_state.py`: Orchestrates interactions between components
    - `persistence.py`: Handles saving/loading data
    - `notification_service.py`: Provides desktop notifications
  - `gui/`: User interface components
    - `main_window.py`: Main application window
    - `widgets/`: Custom UI widgets

## License

[MIT License](LICENSE)
