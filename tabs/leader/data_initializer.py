import streamlit as st

def initialize_leaderboard_data():
    """Initialize session state with sample data matching the database model."""
    
    if 'financial_services' not in st.session_state:
        st.session_state.financial_services = [
            {
                'id': 1,
                'name': 'Discovery Bank',
                'description': 'Digital-first banking with rewards and no monthly fees',
                'category': 'Banking',
                'upvotes': 245,
                'downvotes': 12,
                'recommends': 189,
                'user_voted': None,
                'features': ['No monthly fees', 'Cashback rewards', 'Digital banking', 'Investment platform']
            },
            {
                'id': 2,
                'name': 'Old Mutual',
                'description': 'Comprehensive life insurance and investment solutions',
                'category': 'Insurance',
                'upvotes': 198,
                'downvotes': 23,
                'recommends': 156,
                'user_voted': None,
                'features': ['Life insurance', 'Unit trusts', 'Retirement planning', 'Risk cover']
            },
            {
                'id': 3,
                'name': 'Capitec Bank',
                'description': 'Simple, affordable banking for everyone',
                'category': 'Banking',
                'upvotes': 312,
                'downvotes': 8,
                'recommends': 278,
                'user_voted': None,
                'features': ['Low fees', 'Branch accessibility', 'Simple products', 'Mobile banking']
            },
            {
                'id': 4,
                'name': 'Santam Insurance',
                'description': 'Reliable short-term insurance for your assets',
                'category': 'Insurance',
                'upvotes': 167,
                'downvotes': 19,
                'recommends': 134,
                'user_voted': None,
                'features': ['Motor insurance', 'Home insurance', 'Business cover', 'Travel insurance']
            },
            {
                'id': 5,
                'name': 'FNB',
                'description': 'Full-service banking with innovative digital solutions',
                'category': 'Banking',
                'upvotes': 203,
                'downvotes': 31,
                'recommends': 167,
                'user_voted': None,
                'features': ['eBucks rewards', 'Digital banking', 'Business banking', 'Investment products']
            },
            {
                'id': 6,
                'name': 'Momentum',
                'description': 'Wellness-focused insurance and investment products',
                'category': 'Insurance',
                'upvotes': 143,
                'downvotes': 15,
                'recommends': 112,
                'user_voted': None,
                'features': ['Wellness rewards', 'Life insurance', 'Medical aid', 'Investment solutions']
            },
            {
                'id': 7,
                'name': 'Standard Bank',
                'description': 'Africa\'s largest bank with comprehensive services',
                'category': 'Banking',
                'upvotes': 178,
                'downvotes': 27,
                'recommends': 145,
                'user_voted': None,
                'features': ['International banking', 'Business solutions', 'Investment banking', 'Digital wallet']
            },
            {
                'id': 8,
                'name': 'Sanlam',
                'description': 'Leading financial services group with diverse offerings',
                'category': 'Insurance',
                'upvotes': 134,
                'downvotes': 21,
                'recommends': 98,
                'user_voted': None,
                'features': ['Life insurance', 'Investment products', 'Employee benefits', 'Wealth management']
            }
        ]
    
    if 'community_goals' not in st.session_state:
        st.session_state.community_goals = [
            {
                'id': 1,
                'name': 'Emergency Fund Challenge',
                'description': 'Build 6 months of expenses as emergency fund',
                'category': 'Safety',
                'target_amount': 50000,
                'participants': 1247,
                'completion_rate': 68,
                'avg_progress': 72,
                'created_by': 'FinanceGuru_SA',
                'likes': 892,
                'user_participating': False,
                'tips': [
                    'Start with R100 per month and increase gradually',
                    'Use a separate high-yield savings account',
                    'Automate transfers on payday'
                ]
            },
            {
                'id': 2,
                'name': 'First Home Deposit',
                'description': 'Save for a 20% deposit on your first home',
                'category': 'Asset',
                'target_amount': 200000,
                'participants': 834,
                'completion_rate': 23,
                'avg_progress': 45,
                'created_by': 'PropertyPro_CT',
                'likes': 623,
                'user_participating': True,
                'tips': [
                    'Research different home loan options',
                    'Consider first-time buyer programs',
                    'Save on rent by house-sitting or sharing'
                ]
            },
            {
                'id': 3,
                'name': 'Debt Freedom Journey',
                'description': 'Pay off all consumer debt using snowball method',
                'category': 'Debt Reduction',
                'target_amount': 75000,
                'participants': 2156,
                'completion_rate': 41,
                'avg_progress': 58,
                'created_by': 'DebtFreeLife',
                'likes': 1456,
                'user_participating': False,
                'tips': [
                    'List all debts from smallest to largest',
                    'Pay minimums on all, extra on smallest',
                    'Celebrate small wins to stay motivated'
                ]
            },
            {
                'id': 4,
                'name': 'Retirement Kickstart',
                'description': 'Start retirement savings before age 30',
                'category': 'Investment',
                'target_amount': 100000,
                'participants': 967,
                'completion_rate': 35,
                'avg_progress': 28,
                'created_by': 'RetireEarly_ZA',
                'likes': 734,
                'user_participating': False,
                'tips': [
                    'Take advantage of compound interest',
                    'Contribute to retirement annuity',
                    'Increase contributions with salary increases'
                ]
            },
            {
                'id': 5,
                'name': 'Investment Portfolio Start',
                'description': 'Build your first diversified investment portfolio',
                'category': 'Investment',
                'target_amount': 25000,
                'participants': 1543,
                'completion_rate': 52,
                'avg_progress': 61,
                'created_by': 'InvestmentKing',
                'likes': 1089,
                'user_participating': False,
                'tips': [
                    'Start with low-cost index funds',
                    'Diversify across asset classes',
                    'Don\'t try to time the market'
                ]
            }
        ]
    
    if 'top_contributors' not in st.session_state:
        st.session_state.top_contributors = [
            {
                'username': 'FinanceGuru_SA',
                'total_votes': 1247,
                'goals_created': 8,
                'goals_completed': 12,
                'points': 15600,
                'badge': '🥇 Gold Contributor',
                'streak_days': 89,
                'avatar': '👨‍💼'
            },
            {
                'username': 'SavingsQueen_JHB',
                'total_votes': 978,
                'goals_created': 5,
                'goals_completed': 18,
                'points': 13450,
                'badge': '🥈 Silver Contributor',
                'streak_days': 67,
                'avatar': '👩‍💼'
            },
            {
                'username': 'InvestmentKing',
                'total_votes': 834,
                'goals_created': 12,
                'goals_completed': 9,
                'points': 12890,
                'badge': '🥈 Silver Contributor',
                'streak_days': 45,
                'avatar': '👨‍🎓'
            },
            {
                'username': 'BudgetMaster_CPT',
                'total_votes': 723,
                'goals_created': 3,
                'goals_completed': 15,
                'points': 11200,
                'badge': '🥉 Bronze Contributor',
                'streak_days': 123,
                'avatar': '👩‍🔬'
            },
            {
                'username': 'DebtFreeWarrior',
                'total_votes': 656,
                'goals_created': 7,
                'goals_completed': 11,
                'points': 9870,
                'badge': '🥉 Bronze Contributor',
                'streak_days': 34,
                'avatar': '👨‍🚀'
            },
            {
                'username': 'PropertyPro_CT',
                'total_votes': 589,
                'goals_created': 4,
                'goals_completed': 8,
                'points': 8950,
                'badge': '🏅 Rising Star',
                'streak_days': 28,
                'avatar': '👩‍🏗️'
            }
        ]
    
    # Initialize user voting tracking
    if 'user_service_votes' not in st.session_state:
        st.session_state.user_service_votes = {}
    
    if 'user_goal_likes' not in st.session_state:
        st.session_state.user_goal_likes = set()
