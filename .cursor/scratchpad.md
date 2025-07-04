# SimpleTimerBank - The Time Bank Edition

## Background and Motivation

The project's direction has been revised to create a "Time Bank" application. The core idea is that a user earns time by doing work, deposits that time into a virtual bank, and can then "spend" or "consume" that banked time on leisure activities, like playing video games. This plan replaces all previous versions.

The main features are:
1.  A persistent time balance that acts as the "bank account".
2.  The ability to manually deposit time (the reward for work).
3.  A consumption timer to spend the banked time.
4.  Sound notifications to signal when a consumption session is over.

## Key Challenges and Analysis

1.  **Data Model Refactor**: The existing `TimeBalance` concept must evolve into a `TimeBank` model that supports transactional operations (deposit, withdraw). This is a critical shift in the core logic.
2.  **State Management**: The application state must be carefully managed. We need to prevent situations like spending more time than is available in the bank or ensuring that time is correctly deducted only *after* a session is completed.
3.  **UI/UX for Banking**: The user interface must be intuitive for a banking metaphor. It needs clear areas for viewing the balance, making deposits, and starting a withdrawal (consumption) session.
4.  **Transaction Logic**: The process of starting a timer, having it run, and then debiting the account must be atomic and robust to errors or the application closing prematurely.

## High-level Task Breakdown

The project will be rebuilt in three phases:

*   **Phase 1**: Core Time Bank Logic (The Vault)
*   **Phase 2**: User Interface Implementation (The Bank Teller)
*   **Phase 3**: Advanced Features & UX (Upgrades)

## Project Status Board

### Phase 1: Core Time Bank Logic (The Vault)
- [ ] **Task 1.1**: Redesign `TimeBalance` into `TimeBank`.
  - [ ] Create a `TimeBank` class in `src/simpletimerbank/core/time_bank.py`.
  - [ ] It must manage a single balance value (in seconds).
  - [ ] It must have `deposit(seconds: int)` and `withdraw(seconds: int)` methods.
  - [ ] The `withdraw` method should raise an error if the amount is greater than the balance.
  - [ ] Ensure all logic is covered by pure unit tests in `tests/test_time_bank.py`.
- [ ] **Task 1.2**: Update Persistence and State Management.
  - [ ] Modify `PersistenceService` to save and load the `TimeBank` state.
  - [ ] Update `AppStateManager` to hold an instance of `TimeBank` instead of `TimeBalance`.
  - [ ] Ensure related tests for these modules are updated and pass.

### Phase 2: User Interface Implementation (The Bank Teller)
- [ ] **Task 2.1**: Redesign the Main Window.
  - [ ] The UI should have three clear sections: Balance Display, Deposit Control, and Consumption Control.
- [ ] **Task 2.2**: Implement Balance Display Widget.
  - [ ] A large, clear display showing the current time in the bank.
  - [ ] It should update automatically when the balance changes.
- [ ] **Task 2.3**: Implement Deposit Control Widget.
  - [ ] Input fields to specify hours, minutes, and seconds to deposit.
  - [ ] A "Deposit" button to add the specified time to the bank.
- [ ] **Task 2.4**: Implement Consumption Control Widget.
  - [ ] Input fields to specify the duration of the consumption timer.
  - [ ] A "Start Session" button. This button should be disabled if the requested time is greater than the bank's balance.
  - [ ] The `CountdownTimer` from the existing codebase will be used here.

### Phase 3: Advanced Features & UX (Upgrades)
- [ ] **Task 3.1**: Implement Sound Notifications.
  - [ ] When the consumption timer finishes, play a sound.
  - [ ] This requires adding a sound file to the project assets.
- [ ] **Task 3.2**: (Recommended) Add Transaction History.
  - [ ] Log every deposit and withdrawal with a timestamp.
  - [ ] Create a simple, scrollable view to show this history to the user.
- [ ] **Task 3.3**: (Recommended) Add Quick Action Buttons.
  - [ ] Add buttons for common deposits (e.g., "+30m", "+1h").
  - [ ] Add buttons for common consumption sessions (e.g., "Spend 15m", "Spend 1h").

## Executor's Feedback or Assistance Requests

*This section will be updated by the Executor if any issues arise.*

## Reviewer's Audit & Feedback

*This section is to be filled out by the Reviewer upon completion of all tasks.*

## Lessons

*This section will be updated with key discoveries or solutions.*