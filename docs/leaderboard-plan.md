# Leaderboard Voting Logic Implementation Plan

This document outlines the plan for implementing the leaderboard voting functionality within the BankStat Dashboard, leveraging the existing MongoDB setup for persistent storage.

## 1. Database Schema Design

A new MongoDB collection, `leaderboard_votes`, will be created to store the voting data. Each document in this collection will represent an item that can be voted on and will have the following structure:

-   `item_id` (String): A unique identifier for the financial service or goal.
-   `item_name` (String): The display name of the item (e.g., "Emergency Fund", "Bank X").
-   `item_type` (String): Categorization of the item, either "financial_service" or "financial_goal".
-   `votes` (Integer): The total count of votes for that item. This will be incremented with each vote.
-   `timestamp` (String/Date): The ISO-formatted timestamp of when the vote was last updated.

**Future Enhancement:** To prevent multiple votes from the same user, a `user_id` field could be added, requiring integration with the PropelAuth system. This is not part of the initial implementation.

## 2. Create `utils/leaderboard_db.py`

A new utility file, `leaderboard_db.py`, will be created within the `utils/` directory. This file will encapsulate all MongoDB interactions specifically for the leaderboard feature, promoting modularity and maintainability as per `.windsurfrules`.

It will contain the following functions:

### `record_vote(item_id: str, item_name: str, item_type: str) -> None`

-   **Purpose:** Increments the vote count for a given item or creates a new entry if the item does not exist in the `leaderboard_votes` collection.
-   **Logic:**
    1.  Connects to the `leaderboard_votes` collection using `DatabaseConnection`.
    2.  Uses `update_one` with `upsert=True` to either increment the `votes` field for an existing `item_id` or insert a new document with `votes: 1`.
    3.  Updates the `timestamp` field.

### `get_leaderboard_data(item_type: str) -> list[dict]`

-   **Purpose:** Retrieves all items of a specified type from the `leaderboard_votes` collection, sorted by their vote count in descending order.
-   **Logic:**
    1.  Connects to the `leaderboard_votes` collection.
    2.  Finds documents matching the `item_type`.
    3.  Sorts the results by the `votes` field in descending order.
    4.  Returns a list of dictionaries, each representing an item with its `item_id`, `item_name`, `item_type`, and `votes`.
-   **Caching:** This function will utilize `st.cache_data` to optimize performance and reduce redundant database calls.

## 3. Modify `tabs/leader_board_tab.py`

The `leader_board_tab.py` file will be updated to integrate the voting user interface and display the leaderboard.

### A. Data Retrieval and Initialization

-   Import functions from `utils/leaderboard_db.py`.
-   **Financial Services:** A hardcoded list of sample financial services will be defined for initial voting. In a production environment, this list would typically be dynamic.
-   **Financial Goals:** The existing `st.session_state.financial_goals` will be used as the items for voting in this category.

### B. User Interface for Voting

-   For both "Financial Services" and "Financial Goals" sections:
    -   Each item will be displayed along with its current vote count, fetched from the `leaderboard_votes` collection via `get_leaderboard_data`.
    -   A "Vote" button will be placed next to each item.
    -   When a "Vote" button is clicked:
        -   The `record_vote` function will be called with the appropriate `item_id`, `item_name`, and `item_type`.
        -   Streamlit's `st.rerun()` will be used to refresh the page and display the updated vote counts.
        -   Visual feedback (e.g., `st.success`) will be provided to the user.

### C. Leaderboard Display

-   After votes are cast and retrieved, the items will be displayed in a ranked order based on their `votes` count (highest first).
-   The display will clearly show the rank, item name, and vote count.

## Proposed Workflow

1.  **Create `utils/leaderboard_db.py`:** Implement the `record_vote` and `get_leaderboard_data` functions.
2.  **Modify `tabs/leader_board_tab.py`:** Implement the UI for displaying items, voting buttons, and the ranked leaderboard, utilizing the new `leaderboard_db` utility.
