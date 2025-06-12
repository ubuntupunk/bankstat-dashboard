# Multi-User Authentication and Database Proposal

This document outlines the plan for transitioning the BankStat Dashboard to a multi-user model, incorporating PropelAuth for authentication, Supabase (PostgreSQL) for core user data, and MongoDB for user-specific file storage (CSV and vectors).

## 1. Token-based State Management with PropelAuth

### Current Understanding
PropelAuth handles user authentication and provides tokens (e.g., JWTs) upon successful login. Streamlit applications are inherently stateless, so maintaining user sessions across reruns is crucial. `st.session_state` is the recommended way to manage state in Streamlit.

### Proposed Approach
*   **Authentication Flow:** Ensure the PropelAuth callback correctly receives and processes the authentication tokens.
*   **Token Storage:** Store the PropelAuth user information (e.g., user ID, email, display name) and potentially the access token (if needed for API calls to PropelAuth or other services) in `st.session_state`. This will allow the application to identify the current user across different pages and reruns.
*   **Session Management:** Implement checks at the beginning of protected pages/tabs to verify if the necessary user information exists in `st.session_state`. If not, redirect the user to the login page.
*   **PropelAuth SDK Integration:** Leverage the PropelAuth Python SDK (if available and already in use, which `propelauth_utils.py` suggests) to handle token validation and user information retrieval securely.

## 2. Multi-User Database Handling: Supabase (PostgreSQL) and MongoDB

### Current Understanding
The application currently uploads processed PDF/CSV data to MongoDB. For a multi-user model, each piece of data must be associated with a specific user. The core user interactions, goals, incentives, and budgeting data will reside in Supabase PostgreSQL, while MongoDB will store user-specific CSV and vector data.

### Proposed Approach

#### 2.1 Supabase (PostgreSQL) for Core User Data

*   **Purpose:** Supabase PostgreSQL will be the primary database for managing core user interactions, personal goals, financial incentives, and budgeting information. This includes data that requires relational integrity and complex querying.
*   **Integration:** SQLAlchemy will be used as the ORM to interact with the Supabase PostgreSQL database, as configured in `db/db.py`.
*   **User Identification:** The `user_id` obtained from PropelAuth will be used as a foreign key in relevant Supabase tables to link data to specific users.
*   **Schema Design:** Tables will be designed to store:
    *   User profiles (linked to PropelAuth `user_id`)
    *   Financial goals (e.g., savings targets, debt repayment plans)
    *   Budget categories and allocations
    *   Transaction summaries and categorizations (derived from processed CSV/PDF data, but stored relationally for analysis)
    *   Incentive tracking and rewards

#### 2.2 MongoDB for User-Specific File Storage

*   **Purpose:** MongoDB will be used *solely* for the storage of raw user CSV files and vectors generated from processed PDFs. This leverages MongoDB's flexibility for unstructured and semi-structured document storage, which is ideal for large binary data or JSON representations of vectors.
*   **User Identification:** When a user logs in via PropelAuth, obtain their unique `user_id`. This `user_id` will be included in MongoDB documents to associate data with the specific user.
*   **Database Schema Modification:**
    *   **Data Collections (e.g., `user_files`, `processed_vectors`):** Modify existing or create new collections for user-uploaded files and their derived vectors. Each document in these collections *must* include a `user_id` field, referencing the `propelauth_user_id`.
        *   Example Schema for `user_files` (for raw CSVs):
            ```json
            {
                "_id": ObjectId("..."),
                "user_id": "propelauth_user_id_from_session",
                "original_filename": "my_transactions.csv",
                "upload_date": ISODate("..."),
                "file_content": "base64_encoded_csv_data_or_gridfs_ref", // Raw CSV content
                "status": "processed", // or "pending", "failed"
                "processed_vector_id": ObjectId("...") // Reference to processed vector data
            }
            ```
        *   Example Schema for `processed_vectors` (for vector JSON from PDFs):
            ```json
            {
                "_id": ObjectId("..."),
                "user_id": "propelauth_user_id_from_session",
                "source_file_id": ObjectId("..."), // Reference to original user_file
                "data_type": "vector_json",
                "content": { ... }, // The actual vector JSON data
                "processing_date": ISODate("...")
            }
            ```
*   **Data Ingestion/Retrieval Logic:**
    *   **Uploads:** When a user uploads a PDF/CSV, the processing logic (currently in `pdf_processor.py` and `processing.py`, and the new CSV upload in `tabs/upload_tab.py`) must be updated to include the current user's `user_id` in the MongoDB documents before insertion.
    *   **Retrieval:** All data retrieval queries for raw files and vectors must be filtered by the current user's `user_id` to ensure users only see their own data. This will involve modifying functions in `connection.py` (for MongoDB), `financial_analyzer.py`, and potentially `dashboard_viz.py`.

### Security Considerations:
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
    G -- User Uploads CSV/PDF --> H[Processing Logic (e.g., pdf_processor.py)];
    H --> I[Add user_id to File Data];
    I --> J[Save File Data to MongoDB (with user_id)];
    G -- User Manages Goals/Budget --> K[Supabase Interaction Logic];
    K --> L[Save/Retrieve Core Data from Supabase (with user_id)];
    G -- User Views Dashboard/Reports --> M{Data Source?};
    M -- Core Data --> L;
    M -- File/Vector Data --> J;
    L --> N[Display User-Specific Core Data];
    J --> O[Display User-Specific File/Vector Data];
