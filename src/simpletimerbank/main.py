"""SimpleTimerBank Desktop Application Entry Point.

This module serves as the main entry point for the SimpleTimerBank desktop application.
It initializes the PySide6 application and manages the application lifecycle.
"""

import sys
from typing import Optional

from PySide6.QtWidgets import QApplication


def main(argv: Optional[list[str]] = None) -> int:
    """Main application entry point.
    
    Initializes and runs the SimpleTimerBank desktop application.
    
    Parameters
    ----------
    argv : list[str], optional
        Command line arguments. If None, uses sys.argv.
        
    Returns
    -------
    int
        Application exit code (0 for success, non-zero for error).
        
    Examples
    --------
    >>> # Run the application
    >>> exit_code = main()
    >>> # Run with custom arguments
    >>> exit_code = main(['--debug'])
    """
    if argv is None:
        argv = sys.argv
    
    # Create the Qt application
    app = QApplication(argv)
    app.setApplicationName("SimpleTimerBank")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationName("supersheepbear")
    
    # TODO: Initialize and show main window
    # This will be implemented in Task 3.1
    
    # For now, just display a basic message
    print("SimpleTimerBank application starting...")
    print("GUI components will be implemented in Phase 3")
    
    # TODO: Replace with actual main window show
    # main_window = MainWindow()
    # main_window.show()
    
    # Start the application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 