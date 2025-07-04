# SimpleTimerBank

A simple desktop timer application with a time balance, built with Python and PySide6.

[![Documentation](https://img.shields.io/badge/docs-published-blue)](https://supersheepbear.github.io/SimpleTimerBank/)
[![License](https://img.shields.io/github/license/supersheepbear/SimpleTimerBank)](https://github.com/supersheepbear/SimpleTimerBank/blob/main/LICENSE)

This application provides a time "bank" where you can deposit or withdraw time, and then spend that balance using a built-in countdown timer.

![Screenshot](https://raw.githubusercontent.com/supersheepbear/SimpleTimerBank/main/docs/assets/screenshot.png)

## Download the Application

1.  Click on the following link to download the application zip file:
    **[Download SimpleTimerBank_v1.0.0.zip](https://github.com/supersheepbear/SimpleTimerBank/raw/main/assets/SimpleTimerBank_v1.0.0.zip)**
2.  Unzip the downloaded file.
3.  Run `SimpleTimerBank.exe` from inside the extracted folder.

## For Developers

This project uses [`uv`](https://github.com/astral-sh/uv) (version 0.2.22+ recommended) for package and environment management.

### 1. Install `uv`

If you don't have `uv` installed, run the appropriate command for your OS:

**macOS / Linux:**
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```sh
uv sync
```

### 3. Run the Application from Source

```sh
uv run simpletimerbank
```

For more detailed information, please see the [full documentation](https://supersheepbear.github.io/SimpleTimerBank/).
