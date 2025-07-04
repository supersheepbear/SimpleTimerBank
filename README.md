# Simple Timer Bank 🏦

Simple Timer Bank is a desktop application for managing your personal "free time." It helps you balance productive work with leisure activities like gaming 🎮, watching movies 🍿, or any other hobbies by treating your free time as a resource in a "bank."

![SimpleTimerBank Screenshot](docs/assets/screenshot.png)

## How It Works

-   **Bank Your Time 💰**: Deposit time you've set aside for leisure into your personal time bank.
-   **Spend Your Time ⏳**: When you're ready for a break, start a timer to begin "withdrawing" and consuming your banked time.
-   **Overdraft Feature ⚠️**: If your timer runs out but you're not ready to stop, the app automatically enters "overdraft mode." It will start drawing from your main bank balance, preventing abrupt interruptions while keeping track of the extra time used.
-   **Automatic Refunds 🔄**: If you end a session early, any unused time from the timer is automatically returned to your bank.

## Features

-   **Digital Clock Displays**: Clear, easy-to-read displays for both your bank balance and the active timer.
-   **Intuitive Transaction Controls**:
    -   Deposit, instantly withdraw, or set your bank balance to a specific value.
    -   Use relative preset buttons (`+15m`, `-30m`, etc.) to quickly adjust the transaction amount.
-   **Flexible Timer Controls**: Start, pause, resume, and stop timer sessions with clear, expanding buttons.
-   **Audio-Visual Alerts**: Receive non-blocking system notifications with custom sounds for key events like overdraft activation and bank depletion.
-   **Persistent State**: Your time bank balance is automatically saved when you close the application and reloaded on startup.
-   **Polished UI**: A clean, visually organized interface with distinct sections for different actions.

## Installation

The recommended way to install Simple Timer Bank is via `pip` or `uv`:

```bash
# Using pip
pip install simpletimerbank

# Or using uv
uv add simpletimerbank
```

## Usage

Once installed, you can run the application from your terminal:

```bash
simpletimerbank
```

## Development Setup

If you wish to contribute to the project, follow these steps to set up a development environment.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/SimpleTimerBank.git
    cd SimpleTimerBank
    ```

2.  **Set up a Virtual Environment and Install**:
    This project uses `uv` for package management.
    ```bash
    # Create a virtual environment
    uv venv
    # Activate it (example for Windows PowerShell)
    .venv\Scripts\Activate.ps1
    # Install the project in editable mode with its dependencies
    uv pip install -e .
    ```

3.  **Run the Application from Source**:
    ```bash
    python -m src.simpletimerbank.main
    ```

## Development Tasks

-   **Run Tests**: `make test` or `uv run pytest`
-   **Build Documentation**: `make doc`
-   **Publish Documentation**: `make publish-docs`

## License

This project is licensed under the [MIT License](LICENSE).
