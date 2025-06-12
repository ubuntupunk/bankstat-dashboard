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

#### 2.1.1 Proposed Supabase Schema Additions for Persistence

To persist user-specific data for features like AI expert chats, financial metrics, and insights, the following tables are proposed for `db/model.py` to be stored in Supabase PostgreSQL:

##### AI Chat Messages

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base

class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    role = Column(String, nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
```

##### User Financial Metrics

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.db import Base

class UserFinancialMetric(Base):
    __tablename__ = "user_financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    metric_name = Column(String, nullable=False) # e.g., "total_income", "total_expenses", "net_flow", "savings_rate"
    value = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now()) # Date for which the metric applies
```

##### User Goals and Progress

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base

class UserGoal(Base):
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    goal_name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class GoalProgress(Base):
    __tablename__ = "goal_progress"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("user_goals.id"), nullable=False)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    date = Column(DateTime(timezone=True), server_default=func.now())
    progress_amount = Column(Float, nullable=False) # Amount contributed or current value
    goal = relationship("UserGoal")
```

##### User Financial Insights

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB # For storing JSON data
from sqlalchemy.sql import func
from db.db import Base

class UserFinancialInsight(Base):
    __tablename__ = "user_financial_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    insight_type = Column(String, nullable=False) # e.g., "category_insights", "monthly_trends", "budget_recommendations"
    insight_data = Column(JSONB, nullable=False) # Store the insight content as JSON
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
```

##### Budget Categories

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.db import Base

class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    name = Column(String, nullable=False) # e.g., "Groceries", "Utilities", "Rent"
    allocated_amount = Column(Float, nullable=False) # Amount budgeted for this category
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

##### Incentives and Rewards

```python
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base

class Incentive(Base):
    __tablename__ = "incentives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reward_value = Column(Float, nullable=False) # e.g., points, monetary value
    criteria = Column(Text, nullable=True) # Description of how to earn the incentive
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserReward(Base):
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    incentive_id = Column(Integer, ForeignKey("incentives.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    reward_amount = Column(Float, nullable=False) # Actual amount earned for this instance
    incentive = relationship("Incentive")
```

##### Leaderboard (Financial Services and Votes)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base

class FinancialService(Base):
    __tablename__ = "financial_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ServiceVote(Base):
    __tablename__ = "service_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    service_id = Column(Integer, ForeignKey("financial_services.id"), nullable=False)
    vote_type = Column(String, nullable=False) # e.g., "upvote", "downvote", "recommend"
    voted_at = Column(DateTime(timezone=True), server_default=func.now())
    financial_service = relationship("FinancialService")
```

##### Energy Consumption (Appliances and Consumption Data)

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base

class Appliance(Base):
    __tablename__ = "appliances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID
    name = Column(String, nullable=False) # e.g., "Refrigerator", "Washing Machine"
    appliance_type = Column(String, nullable=True) # e.g., "Kitchen", "Laundry"
    power_rating_watts = Column(Float, nullable=True) # Power consumption in Watts
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EnergyConsumption(Base):
    __tablename__ = "energy_consumption"

    id = Column(Integer, primary_key=True, index=True)
    appliance_id = Column(Integer, ForeignKey("appliances.id"), nullable=False)
    user_id = Column(String, index=True, nullable=False) # PropelAuth user ID (redundant but good for direct queries)
    consumption_kwh = Column(Float, nullable=False) # Energy consumed in kWh for a period
    consumption_date = Column(DateTime(timezone=True), nullable=False) # Date of consumption reading
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    appliance = relationship("Appliance")
```

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
