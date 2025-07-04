# SimpleTimerBank - The Time Bank Edition

## Background and Motivation

The project's goal is to create a "Time Bank" application. A user can store units of time in a "bank" and then "spend" this time via a countdown timer. This allows for disciplined time management, where time must be earned before it can be spent.

The core features required are:
1.  **Time Bank**: A central store for the user's time balance.
2.  **Balance Display**: A clear, visible display of the current time balance.
3.  **Manual Adjustments**: The ability to add or remove time from the bank.
4.  **Consumption Timer**: A timer to spend a specific amount of time withdrawn from the bank. This timer has `Start`, `Pause`, `Resume`, and `Stop` controls.
5.  **Refund on Stop**: If a timer session is stopped early, the unused time is refunded to the bank.
6.  **Overdraft**: If the timer completes its initial cycle and is not stopped, it will continue to run, draining the main bank balance until it hits zero.
7.  **Notifications**: A notification is triggered when the initial timer cycle completes.

## Key Challenges and Analysis

1.  **Stateful Timer Logic**: The `CountdownTimer` is no longer a simple countdown. It must be a state machine that manages `Idle`, `Running`, `Paused`, and `Stopped` states to handle the user controls correctly.
2.  **Timer-Bank Interaction Protocol**: The relationship between the `CountdownTimer` and `TimeBank` is now highly transactional and must be robust.
    -   **Start**: Time must be withdrawn from the bank to fund the timer. This is a hard requirement.
    -   **Stop**: Unused time from the timer's initial duration must be reliably refunded to the bank.
    -   **Overdraft Tick**: During the overdraft phase, the timer must trigger a 1-second withdrawal from the bank on every tick.
3.  **The Overdraft Mechanism**: This is the most complex logic. The `CountdownTimer` must seamlessly transition from its "normal countdown" phase to an "overdraft" phase. This requires a clear state flag (e.g., `is_overdrafting`). The UI must also visually reflect this critical state change.
4.  **UI Decoupling**: The application UI needs to be conceptually split. There should be a "Bank" area for managing the balance and a "Timer" area for the countdown. Both must communicate through a central controller (`AppState`) to remain decoupled and maintainable.
5.  **Atomicity**: Actions like stopping and refunding must be treated as atomic operations to prevent data corruption (e.g., refunding time without actually stopping the timer).

## High-level Task Breakdown

The project will be implemented in phases, focusing on building a robust core logic foundation before the UI.

*   **Phase 1**: Core Logic - The `TimeBank`
*   **Phase 2**: Core Logic - The Advanced `CountdownTimer`
*   **Phase 3**: Core Logic - The `AppState` Orchestrator
*   **Phase 4**: GUI Implementation
*   **Phase 5**: Final Features and Polish

## Project Status Board

### Phase 1: Core Logic - The `TimeBank`
- [x] **Task 1.1**: Implement the `TimeBank` class.
  - [x] Create `src/simpletimerbank/core/time_bank.py` with a `TimeBank` class.
  - [x] The class will manage a single time balance in seconds.
  - [x] Implement `get_balance() -> int`, `deposit(seconds: int)`, and `withdraw(seconds: int)`.
  - [x] `withdraw` must raise a `ValueError` if funds are insufficient.
  - [x] Create `tests/test_time_bank.py` and ensure all methods are fully tested.

### Phase 2: Core Logic - The Advanced `CountdownTimer`
- [x] **Task 2.1**: Implement `CountdownTimer` with internal state management.
  - [x] Create `src/simpletimerbank/core/countdown_timer.py` with a `CountdownTimer` class.
  - [x] Define states: `IDLE`, `RUNNING`, `PAUSED`, `STOPPED`.
  - [x] It should also have a boolean flag: `is_overdrafting`.
  - [x] Implement `start(duration: int)`, `pause()`, `resume()`, and `stop()`.
- [x] **Task 2.2**: Implement the `tick` and overdraft logic.
  - [x] The timer's `tick` method (called every second) should decrement `remaining_seconds`.
  - [x] When `remaining_seconds` hits zero, the timer should set `is_overdrafting` to `True`.
  - [x] In overdraft mode, each `tick` must signal that 1 second should be withdrawn from the bank.
- [x] **Task 2.3**: Create `tests/test_countdown_timer.py` to test all state transitions, the countdown, and the overdraft signaling.

### Phase 3: Core Logic - The `AppState` Orchestrator
- [x] **Task 3.1**: Implement the `AppState` class.
  - [x] Create `src/simpletimerbank/core/app_state.py` with an `AppState` class to manage `TimeBank` and `CountdownTimer` instances.
- [x] **Task 3.2**: Implement the core session logic in `AppState`.
  - [x] `start_session(duration: int)`: Withdraws from bank, then starts the timer. Fails if bank funds are too low.
  - [x] `stop_session()`: Stops the timer, gets its `remaining_seconds`, and deposits them back to the bank.
  - [x] `pause_session()` and `resume_session()`.
- [x] **Task 3.3**: Connect timer signals to `AppState` actions.
  - [x] Handle the overdraft signal from the timer to withdraw 1 second from the `TimeBank`.
  - [x] Handle the timer completion signal to trigger notifications.
- [x] **Task 3.4**: Add persistence to `AppState` to save/load the `TimeBank` balance.
- [x] **Task 3.5**: Update `tests/test_app_state.py` to test these interaction workflows.
  - [x] Add a specific test case to verify that stopping a session early correctly refunds the remaining time to the `TimeBank`.

### Phase 4: GUI Implementation
- [ ] **Task 4.1**: Design and implement the Bank UI section.
- [ ] **Task 4.2**: Design and implement the Timer UI section.
- [ ] **Task 4.3**: Connect GUI controls to the `AppState` methods.
- [ ] **Task 4.4**: Ensure the UI updates based on signals from `AppState` (e.g., balance changes, timer ticks, overdraft mode visuals).

### Phase 5: Final Features and Polish
- [ ] **Task 5.1**: Implement desktop notifications.
- [ ] **Task 5.2**: Refine UI/UX, package, and document the application.

## Executor's Feedback or Assistance Requests
### 2023-10-15: Phase 1 Complete
Phase 1 has been successfully completed. The `TimeBank` class has been implemented following the specifications, with full test coverage. All tests are passing.

The `TimeBank` class provides these core features:
- Initializes with a zero balance
- `deposit(seconds)` method to add time to the bank
- `withdraw(seconds)` method that enforces sufficient funds, raising ValueError if insufficient
- `get_balance()` method to retrieve the current balance
- `set_balance(seconds)` method to directly set the balance

The implementation follows all the required development standards:
- Full NumPy-style docstrings
- Complete type hinting
- PEP 8 compliant code
- Pure unit tests with no I/O
- Tests execute in well under the 5s target time

Next, I will begin implementing Phase 2 - the Advanced `CountdownTimer`.

### 2023-10-16: Phase 2 Complete
Phase 2 has been successfully completed. The `CountdownTimer` class has been completely redesigned following TDD principles. All tests are passing.

The new `CountdownTimer` implementation includes:
- Four clearly defined states: `IDLE`, `RUNNING`, `PAUSED`, and `STOPPED`
- An `is_overdrafting` flag to indicate when the timer has reached zero and is in overdraft mode
- Self-contained time tracking with `_remaining_seconds` (instead of relying on `TimeBalance`)
- A `tick()` method that returns a signal (1 second) when in overdraft mode to communicate with the bank
- Completion callback for notification when the timer transitions to overdraft mode

The implementation addresses the key challenges mentioned in the plan:
- The timer is now a proper state machine with clear transitions and appropriate error handling
- Overdraft detection and signaling are properly implemented
- The timer preserves its state (remaining seconds) when stopped for refund purposes
- Timer and bank logic are now fully decoupled for better separation of concerns

All tests are passing with 100% coverage of the new functionality.

Next, I will begin implementing Phase 3 - the `AppState` Orchestrator.

### 2023-10-17: Phase 3 Complete
Phase 3 has been successfully completed. The `AppState` class has been implemented to orchestrate the interactions between the `TimeBank` and `CountdownTimer`. All tests are passing.

The new `AppState` implementation includes:
- Session management with `start_session()`, `pause_session()`, `resume_session()`, and `stop_session()` methods
- Proper handling of timer signals, including overdraft handling and time refunds
- Integration with the `PersistenceService` to save and load the bank balance
- Event callback hooks for timer ticks and timer completion notifications

Key features implemented:
- The session logic now properly handles the timer lifecycle and bank transactions as atomic operations
- When a session is stopped early, remaining time is correctly refunded to the bank
- When the timer enters overdraft mode, the app state withdraws time from the bank on each tick
- When the bank balance is depleted, the timer is automatically stopped

The `AppState` tests validate all these workflows with comprehensive test cases, including a specific test to verify the refund mechanism. All tests are passing with good coverage.

The implementation successfully addresses the key challenges from the plan:
- Timer-bank interactions are now properly orchestrated
- The overdraft mechanism withdraws time from the bank appropriately
- Transactions (start, stop, refund) are handled atomically
- The UI can be properly decoupled with the callback system

Next, I would begin implementing Phase 4 - GUI Implementation.

## Reviewer's Audit & Feedback
*This section is to be filled out by the Reviewer upon completion of all tasks.*

## Lessons
*This section will be updated with key discoveries or solutions.*