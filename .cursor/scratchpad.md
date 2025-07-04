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
- [ ] **Task 1.1**: Implement the `TimeBank` class.
  - [ ] Create `src/simpletimerbank/core/time_bank.py` with a `TimeBank` class.
  - [ ] The class will manage a single time balance in seconds.
  - [ ] Implement `get_balance() -> int`, `deposit(seconds: int)`, and `withdraw(seconds: int)`.
  - [ ] `withdraw` must raise a `ValueError` if funds are insufficient.
  - [ ] Create `tests/test_time_bank.py` and ensure all methods are fully tested.

### Phase 2: Core Logic - The Advanced `CountdownTimer`
- [ ] **Task 2.1**: Implement `CountdownTimer` with internal state management.
  - [ ] Create `src/simpletimerbank/core/countdown_timer.py` with a `CountdownTimer` class.
  - [ ] Define states: `IDLE`, `RUNNING`, `PAUSED`, `STOPPED`.
  - [ ] It should also have a boolean flag: `is_overdrafting`.
  - [ ] Implement `start(duration: int)`, `pause()`, `resume()`, and `stop()`.
- [ ] **Task 2.2**: Implement the `tick` and overdraft logic.
  - [ ] The timer's `tick` method (called every second) should decrement `remaining_seconds`.
  - [ ] When `remaining_seconds` hits zero, the timer should set `is_overdrafting` to `True`.
  - [ ] In overdraft mode, each `tick` must signal that 1 second should be withdrawn from the bank.
- [ ] **Task 2.3**: Create `tests/test_countdown_timer.py` to test all state transitions, the countdown, and the overdraft signaling.

### Phase 3: Core Logic - The `AppState` Orchestrator
- [ ] **Task 3.1**: Implement the `AppState` class.
  - [ ] Create `src/simpletimerbank/core/app_state.py` with an `AppState` class to manage `TimeBank` and `CountdownTimer` instances.
- [ ] **Task 3.2**: Implement the core session logic in `AppState`.
  - [ ] `start_session(duration: int)`: Withdraws from bank, then starts the timer. Fails if bank funds are too low.
  - [ ] `stop_session()`: Stops the timer, gets its `remaining_seconds`, and deposits them back to the bank.
  - [ ] `pause_session()` and `resume_session()`.
- [ ] **Task 3.3**: Connect timer signals to `AppState` actions.
  - [ ] Handle the overdraft signal from the timer to withdraw 1 second from the `TimeBank`.
  - [ ] Handle the timer completion signal to trigger notifications.
- [ ] **Task 3.4**: Add persistence to `AppState` to save/load the `TimeBank` balance.
- [ ] **Task 3.5**: Update `tests/test_app_state.py` to test these interaction workflows.
  - [ ] Add a specific test case to verify that stopping a session early correctly refunds the remaining time to the `TimeBank`.

### Phase 4: GUI Implementation
- [ ] **Task 4.1**: Design and implement the Bank UI section.
- [ ] **Task 4.2**: Design and implement the Timer UI section.
- [ ] **Task 4.3**: Connect GUI controls to the `AppState` methods.
- [ ] **Task 4.4**: Ensure the UI updates based on signals from `AppState` (e.g., balance changes, timer ticks, overdraft mode visuals).

### Phase 5: Final Features and Polish
- [ ] **Task 5.1**: Implement desktop notifications.
- [ ] **Task 5.2**: Refine UI/UX, package, and document the application.

## Executor's Feedback or Assistance Requests
*This section will be updated by the Executor if any issues arise.*

## Reviewer's Audit & Feedback
*This section is to be filled out by the Reviewer upon completion of all tasks.*

## Lessons
*This section will be updated with key discoveries or solutions.*