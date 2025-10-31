# Multi-Delete Session Feature

## Summary
Enhanced the session history management with checkbox-based selection for deleting single, multiple, or all sessions at once.

## New Features

### 1. Checkbox Selection System (Lines 1000-1015)
Each session in the history now has a checkbox next to it, allowing you to:
- Click individual checkboxes to select specific sessions
- View session information inline for easy identification
- Select as many sessions as you want before deleting

### 2. Management Buttons (Lines 957-998)

#### **Select All Button**
- Instantly selects all sessions in the history
- Useful when you want to delete everything or most items

#### **Deselect All Button**
- Clears all selections
- Useful for starting over with your selection

#### **Delete Selected (N) Button**
- Only appears when at least one session is selected
- Shows the count of selected sessions: `Delete Selected (3)`
- Deletes all selected sessions in one action
- Displays success message with count deleted
- Primary button styling (highlighted)

#### **Delete All (N) Button**
- Shows total number of sessions: `Delete All (15)`
- **Two-step confirmation process:**
  1. Click "Delete All" → Shows warning dialog
  2. Confirm with "Yes, Delete All" or "Cancel"
- Safety feature to prevent accidental mass deletion
- Secondary button styling initially

### 3. Removed Old Delete Button
- Removed the single "Delete this session" button from the session details view
- All deletion is now managed through the checkbox system at the top

## User Interface Flow

### Deleting Single Session
1. Check the box next to the session you want to delete
2. Click "Delete Selected (1)"
3. Session is immediately deleted

### Deleting Multiple Sessions
1. Check boxes next to all sessions you want to delete
2. Or click "Select All" and then uncheck ones you want to keep
3. Click "Delete Selected (N)" where N is your selection count
4. All selected sessions are deleted

### Deleting All Sessions
1. Click "Delete All (N)" button
2. Warning appears: "⚠️ Confirm: Delete ALL sessions?"
3. Click "Yes, Delete All" to proceed, or "Cancel" to abort
4. All sessions are deleted if confirmed

## Technical Implementation

### Session State Management
- Uses Streamlit's `session_state` to track selected sessions
- `selected_sessions`: Set of filenames currently selected
- `confirm_delete_all`: Boolean flag for delete-all confirmation dialog

### Data Persistence
- Selections are maintained during page interactions
- After deletion, selections are cleared and page refreshes
- No sessions are deleted until you click a delete button

### Visual Feedback
- Success messages show count of deleted sessions
- Button types:
  - Primary (red): Delete Selected
  - Secondary (gray): Delete All (initial state)
  - Primary (red): Yes, Delete All (confirmation)

## Example Usage Scenarios

### Scenario 1: Clean up failed sessions
```
1. Look through the list for sessions with negative profit
2. Check boxes next to those sessions
3. Click "Delete Selected (5)"
```

### Scenario 2: Remove old test runs
```
1. Click "Select All"
2. Uncheck the 3 most recent sessions you want to keep
3. Click "Delete Selected (12)"
```

### Scenario 3: Start fresh
```
1. Click "Delete All (15)"
2. Review the warning
3. Click "Yes, Delete All"
```

## Safety Features
- Two-step confirmation for "Delete All"
- Visual warning indicator (⚠️) before mass deletion
- Cancel option at every step
- Success messages confirm number of sessions deleted
- Immediate page refresh shows updated list

## Benefits
- **Faster cleanup**: Delete multiple sessions at once instead of one-by-one
- **More control**: Choose exactly which sessions to keep or remove
- **Safer**: Confirmation dialog prevents accidental bulk deletion
- **Better UX**: Visual feedback and clear button labels
- **More organized**: Easy-to-scan list with checkboxes
