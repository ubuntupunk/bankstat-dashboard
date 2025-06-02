# BankStat Dashboard

A Streamlit app for analyzing bank statements and visualizing financial data.

## Project Overview

The BankStat Dashboard is a Streamlit application designed to help users analyze their bank statements and gain insights into their financial activity. It provides features for uploading bank statement data, processing transactions, and visualizing key financial metrics. The app integrates with MongoDB for data persistence and offers a user-friendly interface for exploring financial trends.

## Features

- Upload bank statement data in JSON format
- Process transactions and extract key financial information
- Visualize financial data using interactive charts and graphs
- Store and retrieve data from MongoDB
- Calculate monthly average balance and other financial metrics
- Display recent transactions with detailed information

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd bankstat-dashboard
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure MongoDB:

   - Ensure you have a MongoDB instance running.
   - Update the MongoDB connection details in `config.py` with your MongoDB URI, database name, and collection name.

4. Set up environment variables:

   - Create a `.env` file based on the `.env.example` file and update the values with your specific configuration.

## Usage

1. Run the Streamlit app:

   ```bash
   streamlit run streamlit_app.py
   ```

2. Open the app in your browser at the address displayed in the terminal (usually `http://localhost:8501`).

3. Upload your bank statement data in JSON format using the file uploader.

4. Click the "Save to Database" button to store the data in MongoDB.

5. Explore the dashboard to visualize your financial data and analyze your transactions.

## File Structure

```
bankstat-dashboard/
├── .env.example          # Example environment variables
├── .gitignore            # Specifies intentionally untracked files that Git should ignore
├── .windsurfrules        # Project-specific rules and configurations
├── bankstatgreen.png     # Project logo
├── config.py             # Configuration settings for the app
├── financial_analyzer.py # Class for analyzing financial data
├── LICENSE               # License information
├── README.md             # This file - project documentation
├── requirements.txt      # List of Python dependencies
├── streamlit_app.py      # Main Streamlit app entry point
├── streamlit_components.py # Custom Streamlit components
├── styles.css            # CSS styles for the app
├── TASK.md               # List of tasks and their status
├── utils.py              # Utility functions
└── data/                 # Directory for storing data files
```

## Contributing

Contributions are welcome! To contribute to the BankStat Dashboard project, follow these steps:

1. Fork the repository.

2. Create a new branch for your feature or bug fix.

3. Make your changes and commit them with descriptive commit messages.

4. Test your changes thoroughly.

5. Submit a pull request with a clear explanation of your changes.
