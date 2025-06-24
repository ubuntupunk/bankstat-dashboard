# BankStat - AI-Powered Financial Analysis Dashboard

A comprehensive Streamlit-based financial analysis application that combines AI, machine learning, and advanced analytics to help users understand their financial data and make informed decisions.

## 🌟 Project Overview

BankStat is a sophisticated financial analysis platform that transforms raw bank statement data into actionable insights. Built with modern technologies including AI-powered advisors, machine learning categorization, and interactive visualizations, BankStat provides users with a complete financial management solution.

### 🎯 Key Capabilities

- **AI Financial Advisor**: Chat with an AI assistant powered by Cerebras Cloud SDK for personalized financial guidance
- **Smart Transaction Categorization**: ML-powered automatic categorization using TensorFlow and scikit-learn
- **Financial Goal Tracking**: Set, monitor, and achieve financial goals with intelligent budgeting tools
- **Community Features**: Leaderboards, voting, and community-driven financial insights
- **Advanced Analytics**: Predictive spending analysis and financial health metrics
- **Service Comparisons**: Compare banking, insurance, and other financial services
- **Financial Calculators**: Bond, investment, and energy cost calculators

## 🚀 Features

### 📊 Core Financial Analysis
- **PDF & CSV Upload**: Process bank statements with intelligent data extraction
- **Interactive Dashboards**: Real-time financial metrics and visualizations
- **Transaction Management**: Categorize, search, and analyze transactions
- **Cash Flow Analysis**: Track income, expenses, and financial trends
- **Balance Tracking**: Monitor account balances and running totals

### 🤖 AI & Machine Learning
- **AI Financial Advisor**: Natural language financial guidance using Cerebras LLM
- **ML Transaction Categorization**: Automatic categorization with confidence scoring
- **Spending Predictions**: ML-powered forecasting of future expenses
- **Custom Model Training**: Train personalized categorization models

### 🎯 Financial Planning
- **Goal Setting**: Create and track financial objectives
- **Budget Management**: Set budgets and monitor spending against targets
- **Progress Tracking**: Visual progress indicators and milestone alerts
- **Incentive System**: Gamified rewards for achieving financial goals

### 🏦 Service Integration
- **Banking Comparison**: Compare banking services and rates
- **Insurance Options**: Explore insurance products and pricing
- **Legal Services**: Access to financial legal services
- **Gym Memberships**: Health and wellness service comparisons

### 🛠️ Financial Tools
- **Bond Calculator**: Calculate bond yields and returns
- **Investment Calculator**: Analyze investment scenarios
- **Energy Calculator**: Estimate energy costs and savings
- **General Financial Calculator**: Various financial computations

### 🏅 Community Features
- **Leaderboards**: Community rankings and achievements
- **Voting System**: Community-driven service recommendations
- **Shared Goals**: Collaborative financial objectives
- **Analytics Dashboard**: Community insights and trends

## 🔧 Technology Stack

### Core Framework
- **Streamlit**: Modern web application framework
- **Python 3.11**: Primary programming language

### AI & Machine Learning
- **Cerebras Cloud SDK**: AI-powered financial advisor
- **TensorFlow**: Deep learning for transaction categorization
- **scikit-learn**: Traditional ML algorithms
- **Pandas & NumPy**: Data processing and analysis

### Databases
- **MongoDB**: Primary data storage for transactions and statements
- **PostgreSQL/Supabase**: Structured data for categories and analytics
- **SQLAlchemy**: ORM for database operations

### Authentication & Security
- **PropelAuth**: OAuth2-based user authentication
- **Session Management**: Secure user session handling

### Visualization & UI
- **Plotly**: Interactive charts and graphs
- **Altair**: Statistical visualizations
- **Custom CSS**: Responsive design and styling

### Deployment
- **Koyeb**: Primary cloud deployment platform
- **Heroku**: Alternative deployment option
- **Docker**: Containerized development environment

## 📁 Project Structure

```
bankstat/
├── streamlit_app.py          # Main application entry point
├── config.py                 # Configuration management
├── financial_analyzer.py     # Core financial analysis engine
├── pdf_processor.py          # PDF bank statement processing
├── processing.py             # Data processing utilities
├── dashboard_viz.py          # Dashboard visualization components
├── requirements.txt          # Python dependencies
├── koyeb.yaml               # Koyeb deployment configuration
├── Procfile                 # Heroku deployment configuration
├── .devcontainer/           # Development container setup
│   └── devcontainer.json
├── components/              # Reusable UI components
│   └── footer.py
├── db/                      # Database layer
│   ├── connection.py        # MongoDB connection management
│   ├── model.py            # SQLAlchemy data models
│   ├── category_db.py      # Category management
│   ├── init_db.py          # Database initialization
│   └── migrations/         # Database migration scripts
├── models/                  # ML models and processors
│   ├── transaction_categorizer.py  # ML categorization engine
│   ├── ml_processor.py     # ML processing interface
│   ├── analyzer_enhancer.py # ML-enhanced analyzers
│   └── ui_components.py    # ML UI components
├── pages/                   # Streamlit pages
│   ├── dashboard.py        # Main dashboard page
│   ├── login.py           # Authentication page
│   ├── privacy.py         # Privacy policy
│   └── tos.py             # Terms of service
├── tabs/                    # Dashboard tab components
│   ├── dashboard_tab.py    # Main dashboard orchestrator
│   ├── upload_tab.py       # File upload interface
│   ├── settings_tab.py     # Application settings
│   ├── expert/             # AI advisor functionality
│   │   └── ai_expert_tab.py
│   ├── goals/              # Financial goals system
│   │   ├── goals_tab.py
│   │   ├── budget_management.py
│   │   └── goals_overview.py
│   ├── leader/             # Community features
│   │   ├── leader_board_main.py
│   │   ├── community_goals.py
│   │   └── voting_analytics.py
│   ├── metrics/            # Financial metrics
│   │   └── key_metrics_tab.py
│   ├── ml/                 # ML integration
│   │   └── ml_integration.py
│   ├── predictions/        # Spending predictions
│   │   └── spending_predictor.py
│   ├── services/           # Service comparisons
│   │   ├── services_tab.py
│   │   ├── banking_tab.py
│   │   └── insurance_tab.py
│   └── tools/              # Financial calculators
│       ├── tools_tab.py
│       ├── bond_calc.py
│       ├── invest_calc.py
│       └── energy_calc.py
├── utils/                   # Utility functions
│   └── utils.py
└── docs/                    # Documentation
    ├── ai_overview.md
    └── project-notes.md
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.11 or higher
- MongoDB instance (local or cloud)
- Git

### 1. Clone the Repository
```bash
git clone <repository_url>
cd bankstat
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.streamlit/secrets.toml` based on `secrets.example.toml`:

```toml
[database]
db_username = "YOUR_DB_USERNAME"
db_password = "YOUR_DB_PASSWORD"
mongodb_url = "YOUR_MONGODB_URL"

[upstage]
api_key = "YOUR_UPSTAGE_API_KEY"

[auth]
client_id = "YOUR_PROPELAUTH_CLIENT_ID"
api_key = "YOUR_PROPELAUTH_API_KEY"
client_secret = "YOUR_PROPELAUTH_CLIENT_SECRET"
auth_url = "YOUR_PROPELAUTH_AUTH_URL"
server_metadata_url = "YOUR_PROPELAUTH_AUTH_URL/.well-known/openid-configuration"
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "YOUR_RANDOM_COOKIE_SECRET"

[cerebras]
api_key = "YOUR_CEREBRAS_API_KEY"

[debug]
debug = "off"  # Set to "on" for debug mode
```

### 4. Initialize Database
```bash
python db/init_db.py
```

### 5. Run the Application
```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`.

## 🚀 Deployment

### Koyeb (Recommended)
1. Configure `koyeb.yaml` with your settings
2. Deploy using Koyeb CLI or web interface
3. Set environment variables in Koyeb dashboard

### Heroku
1. Install Heroku CLI
2. Create new Heroku app: `heroku create your-app-name`
3. Set environment variables: `heroku config:set VAR_NAME=value`
4. Deploy: `git push heroku main`

### Streamlit Cloud
1. Connect your GitHub repository
2. Configure secrets in Streamlit Cloud dashboard
3. Deploy directly from the web interface

## 📖 Usage Guide

### Getting Started
1. **Sign Up/Login**: Create an account using PropelAuth authentication
2. **Upload Data**: Navigate to "Upload & Process" to upload bank statements (PDF or CSV)
3. **Explore Dashboard**: View financial metrics, trends, and insights
4. **Set Goals**: Create financial goals and budgets in the "Goals" section
5. **Ask AI**: Chat with the AI financial advisor for personalized advice

### Key Features Walkthrough

#### 📊 Dashboard
- View key financial metrics and KPIs
- Analyze spending patterns and trends
- Monitor account balances and cash flow

#### 🤖 AI Advisor
- Ask questions about budgeting, saving, and investing
- Get personalized financial advice
- Receive guidance in South African Rand (ZAR) context

#### 🎯 Goals & Budgeting
- Set financial goals with target amounts and deadlines
- Create and monitor budgets by category
- Track progress with visual indicators

#### 🛠️ Financial Tools
- **Bond Calculator**: Calculate bond yields and investment returns
- **Investment Calculator**: Analyze different investment scenarios
- **Energy Calculator**: Estimate energy costs and potential savings

#### 🏦 Service Comparisons
- Compare banking services and interest rates
- Explore insurance options and pricing
- Find legal and wellness services

## 🔧 Development

### Development Environment
Use the provided dev container for consistent development:
```bash
# Using VS Code with Dev Containers extension
code .
# Select "Reopen in Container" when prompted
```

### Code Style
- Follow PEP8 guidelines (88 character line length)
- Use type hints for better code clarity
- Add docstrings for all functions and classes
- Maximum function length: 50 lines

### Testing
```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Follow existing code patterns and conventions
3. Add appropriate tests
4. Update documentation
5. Submit pull request

## 🛡️ Security & Privacy

### Data Protection
- All financial data is encrypted in transit and at rest
- User authentication handled by PropelAuth OAuth2
- No sensitive data stored in application logs
- POPIA compliance for South African users

### API Security
- API keys stored securely in environment variables
- Rate limiting implemented for external API calls
- Input validation on all user-provided data

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code style guidelines** (see `.windsurfrules`)
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Submit a Pull Request**

### Development Guidelines
- Read the `.agent.md` files in each directory for module-specific guidance
- Follow the existing architecture patterns
- Ensure all tests pass before submitting PR
- Update relevant documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: Check the `docs/` directory and `.agent.md` files
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Community**: Join discussions in GitHub Discussions

## 🙏 Acknowledgments

- **Cerebras Cloud SDK** for AI-powered financial advice
- **PropelAuth** for secure authentication
- **Streamlit** for the amazing web framework
- **MongoDB** and **Supabase** for data storage solutions
- **TensorFlow** and **scikit-learn** for machine learning capabilities

---

*Built with ❤️ for better financial understanding and management*
