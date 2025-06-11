# Multi-User Authentication and Database Proposal

This document outlines the plan for transitioning the BankStat Dashboard to a multi-user model, incorporating PropelAuth for authentication and MongoDB for user-specific data storage.

## 1. Token-based State Management with PropelAuth

### Current Understanding
PropelAuth handles user authentication and provides tokens (e.g., JWTs) upon successful login. Streamlit applications are inherently stateless, so maintaining user sessions across reruns is crucial. `st.session_state` is the recommended way to manage state in Streamlit.

### Proposed Approach
*   **Authentication Flow:** Ensure the PropelAuth callback correctly receives and processes the authentication tokens.
*   **Token Storage:** Store the PropelAuth user information (e.g., user ID, email, display name) and potentially the access token (if needed for API calls to PropelAuth or other services) in `st.session_state`. This will allow the application to identify the current user across different pages and reruns.
*   **Session Management:** Implement checks at the beginning of protected pages/tabs to verify if the necessary user information exists in `st.session_state`. If not, redirect the user to the login page.
*   **PropelAuth SDK Integration:** Leverage the PropelAuth Python SDK (if available and already in use, which `propelauth_utils.py` suggests) to handle token validation and user information retrieval securely.

## 2. Multi-User Database Handling with MongoDB

### Current Understanding
The application currently uploads processed PDF/CSV data to MongoDB. For a multi-user model, each piece of data (bank statement, processed JSON, vector JSON) must be associated with a specific user.

### Proposed Approach
*   **User Identification:** When a user logs in via PropelAuth, obtain their unique `user_id` from PropelAuth. This `user_id` will be the primary key for associating data with users in MongoDB.
*   **Database Schema Modification:**
    *   **User Collection (Optional but Recommended):** Create a `users` collection in MongoDB to store basic user metadata (e.g., `propelauth_user_id`, `email`, `display_name`, `created_at`). This can serve as a central point for user-specific data and relationships, even if PropelAuth is the primary source of truth for authentication.
    *   **Data Collections (e.g., `bank_statements`, `processed_data`):** Modify existing or create new collections for bank statements and processed data. Each document in these collections *must* include a `user_id` field, referencing the `propelauth_user_id`.
        *   Example Schema for `bank_statements`:
            ```json
            {
                "_id": ObjectId("..."),
                "user_id": "propelauth_user_id_from_session",
                "original_filename": "my_bank_statement.pdf",
                "upload_date": ISODate("..."),
                "raw_pdf_data_ref": "path_to_s3_or_gridfs_if_stored_raw", // If raw PDFs are stored
                "status": "processed", // or "pending", "failed"
                "processed_data_id": ObjectId("...") // Reference to processed data
            }
            ```
        *   Example Schema for `processed_data` (for vector JSON, CSV to JSON):
            ```json
            {
                "_id": ObjectId("..."),
                "user_id": "propelauth_user_id_from_session",
                "bank_statement_id": ObjectId("..."), // Reference to original statement
                "data_type": "vector_json", // or "csv_json"
                "content": { ... }, // The actual processed JSON data
                "processing_date": ISODate("...")
            }
            ```
*   **Data Ingestion/Retrieval Logic:**
    *   **Uploads:** When a user uploads a PDF/CSV, the processing logic (currently in `pdf_processor.py` and `processing.py`, and the new CSV upload in `tabs/upload_tab.py`) must be updated to include the current user's `user_id` in the MongoDB documents before insertion.
    *   **Retrieval:** All data retrieval queries (e.g., for the dashboard, AI expert tab) must be filtered by the current user's `user_id` to ensure users only see their own data. This will involve modifying functions in `connection.py`, `financial_analyzer.py`, and potentially `dashboard_viz.py`.
*   **Security Considerations:**
    *   **Server-Side Validation:** Always validate the `user_id` on the server-side (or in the backend logic of the Streamlit app) to prevent users from accessing data belonging to others by manipulating client-side requests.
    *   **Least Privilege:** Ensure that database queries only fetch data relevant to the authenticated user.

## High-Level Workflow Diagram:

```mermaid
graph TD
    A[User Accesses App] --> B{Is User Authenticated?};
    B -- No --> C[Redirect to PropelAuth Login];
    C --> D[PropelAuth Authenticates User];
    D --> E[PropelAuth Redirects to Callback with Tokens];
    E --> F[App Processes Tokens & Stores User Info in st.session_state];
    F --> G[User Accesses Protected Pages/Features];
    G --> H{User Uploads Data (PDF/CSV)};
    H --> I[Processing Logic (e.g., pdf_processor.py)];
    I --> J[Add user_id to Data];
    J --> K[Save Data to MongoDB (with user_id)];
    G --> L{User Views Dashboard/Reports};
    L --> M[Retrieve Data from MongoDB (filtered by user_id)];
    M --> N[Display User-Specific Data];
