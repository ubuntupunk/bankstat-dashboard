### 2025-06-02
- [x] Handle 'StreamlitBankProcessor' object has no attribute 'process_latest_json' error. (Completed)
- [x] Handle cases where no bank statement JSON objects exist in the database. (Completed)
- [x] Corrected 'FinancialAnalyzer' object has no attribute 'process_latest_json' error in Recent Transactions section. (Completed)
- [ ] Compare 'streamlit_app.py' and 'app.py' for PDF processing and data display, specifically addressing missing balance and running totals.
- [ ] on streamlit-cloud branch After password reset, failed to return to login page https://35258265.propelauthtest.com/propelauth/oauth/authorize?response_type=code&client_id=3464455f14962ddf38e620b643c7f85a&redirect_uri=http%3A%2F%2Flocalhost%3A8501%2Foauth2callback&scope=openid+email+profile&state=mEPKtc2ENywcKAa4hBCLbhsvBYgzkp&nonce=wHrj4PeKNNnrYGp6i456&code_challenge=5bYtaMRjzgBswOtVt0MK32Q0bogpid58HmAkKcAM5tM&code_challenge_method=S256

- [ ] on streamlit-cloud branch After login flow, failed to login https://35258265.propelauthtest.com/propelauth/oauth/authorize?response_type=code&client_id=3464455f14962ddf38e620b643c7f85a&redirect_uri=http%3A%2F%2Flocalhost%3A8501%2Foauth2callback&scope=openid+email+profile&state=UhzY2V1OAFbeJCixK6Cs6Oc0FdzCqJ&nonce=Fd5bwewLt97sSDlORlTf&code_challenge=CeixcfcPgiPSPenV4lvneknOliPGD5gsafn-kJMc07w&code_challenge_method=S256


### Plan for Streamlit App Improvements (2025-06-02)

**Phase 1: Data Persistence and Loading**

**Goal 1: Integrate MongoDB upload into `streamlit_app.py`'s "Save to Database" button.**
*   **Current State:** The "Save to Database" button in `streamlit_app.py` currently saves the processed JSON to a local file named `latest_bank_statement.json`.
*   **Proposed Change:** Adapt the `upload_to_mongodb` function from `app.py` and integrate it into `streamlit_app.py`. This will ensure that when a user clicks "Save to Database", the processed bank statement JSON is also uploaded to your MongoDB database.
*   **Feedback:** Add a visual confirmation (a Streamlit success toast) to indicate that the data has been successfully saved to the database.

**Goal 2: Ensure `streamlit_app.py` correctly loads data for the dashboard.**
*   **Current State:** The dashboard in `streamlit_app.py` currently relies on `StreamlitBankProcessor.process_latest_json()` which loads from the local `latest_bank_statement.json`. This seems to be causing the "No bank statement JSON found" message if the local file isn't present or correctly accessed.
*   **Proposed Change:** Modify the `FinancialAnalyzer` class (located in `../Projects/bankstat/tools/financial_analyzer_with_cats.py`) to first check for the `latest_bank_statement.json` file in the `bankstat-dashboard` directory (where `streamlit_app.py` resides). If that file is not found, it will then fall back to looking for the latest JSON file in the `output/` directory (which is where `app.py` typically saves its processed JSONs). This ensures the `FinancialAnalyzer` can always find the most recently processed data, whether it's from the Streamlit app's local save or from the original `app.py`'s output.
*   **Proposed Change:** Update `streamlit_app.py` to use `analyzer.process_latest_json()` directly for fetching transaction data for the dashboard, rather than relying on `processor.process_latest_json()`. This will leverage the `FinancialAnalyzer`'s robust data loading and parsing capabilities, including its ability to connect to MongoDB.

### Phase 2: Data Processing and Display

**Goal 3: Verify `FinancialAnalyzer`'s data extraction and calculation.**
*   **Current State:** You mentioned "losing the balance and running totals." My analysis of `financial_analyzer_with_cats.py` shows that its `_extract_transactions` method explicitly looks for and parses a "Balance (R)" column from the raw HTML tables. It also combines debits and fees into a `total_debits` column.
*   **Verification:** Confirm that this parsing logic is correctly applied when `FinancialAnalyzer` processes the data. The issue is likely in how the data is *fed* to `FinancialAnalyzer` in `streamlit_app.py`, rather than a flaw in `FinancialAnalyzer`'s core calculation logic itself.

**Goal 4: Update `streamlit_app.py` to display balance and running totals.**
*   **Proposed Change:** Ensure that the "Recent Transactions" table in `streamlit_app.py` explicitly includes the `balance` column, making it visible to the user. The `FinancialAnalyzer`'s `calculate_monthly_average_balance` method should then correctly use this data for the "Avg Balance" metric.

This plan aims to restore the full functionality of data persistence and correct display of financial metrics, including balances and running totals, by ensuring the Streamlit app properly integrates with the `FinancialAnalyzer` and MongoDB.

# Please fix
[] In Dashboard side panel, on first login. The widget with key "dashboard_start_date" was created with a default value but also had its value set via the Session State API. I need to refresh page for it to show up.

# Completed

- [x] Fixed unterminated string literal in 'financial_analyzer.py'
- [x] Ensured "Upload to Database" button uses MongoDB credentials from 'financial_analyzer.py'
- [x] Re-introduced debug and processing information for MongoDB upload in 'streamlit_app.py'
- [x] Resolved "DataFrame has column names of mixed type" warning in 'streamlit_app.py'
- [x] Ensured MongoDB upload debug messages are visible in 'streamlit_app.py'
- [x] Add streamlit caching methods to persist data and db connections. Eg @st.cache_data (2025-06-02)
- [ ] We need a TOS page (2025-06-05)
