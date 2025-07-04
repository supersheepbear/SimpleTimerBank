# Usage Guide

This guide covers how to run the SimpleTimerBank application from source and how to build the standalone executable.

## Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) build tool
- `make` (optional, for convenience)

## Running from Source

Running the application directly from the source code is the quickest way to get started.

1.  **Install Dependencies**:
    First, sync the project dependencies using `uv`.
    ```sh
    uv sync
    ```

2.  **Run the Application**:
    Use the `uv run` command to execute the main script.
    ```sh
    uv run simpletimerbank
    ```
    The application GUI should appear on your screen.

## Building the Executable

The project is configured to build a standalone executable (`.exe` on Windows) that bundles the application and all its dependencies.

We support two build modes:

### 1. Fast-Starting Folder Mode (for Development)

This is the **recommended** mode for development and testing. It creates a folder containing the `.exe` and all its dependencies. This version starts almost instantly.

```sh
make build-exe
```

After the build completes, you will find the executable inside the `dist/SimpleTimerBank/` directory.

### 2. Single-File Mode (for Distribution)

This mode creates a single, self-contained `.exe` file. This is convenient for sharing, but be aware that it will have a **slower startup time** as it needs to decompress itself into a temporary directory every time it runs.

```sh
make build-exe-dist
```

After the build completes, you will find `SimpleTimerBank.exe` inside the `dist/` directory. 