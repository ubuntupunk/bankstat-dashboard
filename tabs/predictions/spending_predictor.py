import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, timedelta
import warnings
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
warnings.filterwarnings('ignore')

class SpendingPredictor:
    def __init__(self, analyzer, db_connection):
        self.analyzer = analyzer
        self.db_connection = db_connection
        self.model = None
        self.scaler = None
        self.imputer = None
        self.features = []
        
    def load_data_from_mongodb(self):
        """Load transaction data from MongoDB"""
        try:
            if self.db_connection:
                collection = self.db_connection.get_collection()
                if collection:
                    # Query all transactions
                    cursor = collection.find({})
                    data = list(cursor)
                    
                    if data:
                        df = pd.DataFrame(data)
                        # Convert to required format
                        return self._process_mongodb_data(df)
            return None
        except Exception as e:
            st.warning(f"MongoDB load failed: {str(e)}")
            return None
    
    def load_data_from_json(self):
        """Fallback to load data from latest_bank_statement.json"""
        try:
            json_path = "latest_bank_statement.json"
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
                return self._process_json_data(df)
            return None
        except Exception as e:
            st.warning(f"JSON load failed: {str(e)}")
            return None
    
    def _process_mongodb_data(self, df):
        """Process MongoDB data into required format"""
        if df.empty:
            return None
            
        # Expected MongoDB structure - adjust based on your schema
        processed_data = []
        
        for _, row in df.iterrows():
            # Convert date
            if 'date' in row:
                date_val = pd.to_datetime(row['date'], errors='coerce')
            else:
                continue
                
            # Get amounts - adjust field names based on your schema
            debit = float(row.get('debits', 0) or 0)
            credit = float(row.get('credits', 0) or 0)
            
            processed_data.append({
                'date': date_val,
                'debits': debit,
                'credits': credit,
                'net_spending': debit - credit,
                'description': row.get('description', ''),
                'category': row.get('category', 'Unknown')
            })
        
        result_df = pd.DataFrame(processed_data)
        result_df = result_df.dropna(subset=['date'])
        result_df = result_df.sort_values('date')
        
        return self._aggregate_daily_data(result_df)
    
    def _process_json_data(self, df):
        """Process JSON data into required format"""
        if df.empty:
            return None
            
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.sort_values('date')
        
        # Ensure numeric columns
        for col in ['debits', 'credits']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['net_spending'] = df['debits'] - df['credits']
        
        return self._aggregate_daily_data(df)
    
    def _aggregate_daily_data(self, df):
        """Aggregate transaction data by day for prediction"""
        if df.empty:
            return None
            
        daily_agg = df.groupby(df['date'].dt.date).agg({
            'debits': 'sum',
            'credits': 'sum',
            'net_spending': 'sum'
        }).reset_index()
        
        daily_agg['date'] = pd.to_datetime(daily_agg['date'])
        daily_agg = daily_agg.sort_values('date')
        
        # Add total_spending column (using debits as spending)
        daily_agg['total_spending'] = daily_agg['debits']
        
        return daily_agg
    
    def load_data(self):
        """Load data with MongoDB primary, JSON fallback"""
        # Try MongoDB first
        df = self.load_data_from_mongodb()
        
        if df is None or df.empty:
            st.info("📱 Using fallback data source...")
            df = self.load_data_from_json()
        else:
            st.success("📊 Loaded data from MongoDB")
            
        if df is None or df.empty:
            st.error("❌ No data available from any source")
            return None
            
        return df
    
    def engineer_features(self, df):
        """Extract temporal features and prepare data"""
        if df.empty:
            return df
            
        df = df.copy()
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_year'] = df['date'].dt.dayofyear
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['day_of_month'] = df['date'].dt.day
        
        # Add lag features (previous spending)
        df['lag_spending_1'] = df['total_spending'].shift(1)
        df['lag_spending_2'] = df['total_spending'].shift(2)
        df['lag_spending_3'] = df['total_spending'].shift(3)
        
        # Add rolling averages
        df['rolling_avg_7'] = df['total_spending'].rolling(window=7, min_periods=1).mean()
        df['rolling_avg_30'] = df['total_spending'].rolling(window=30, min_periods=1).mean()
        
        # Add seasonal features
        df['quarter'] = df['date'].dt.quarter
        df['is_month_start'] = (df['date'].dt.day <= 5).astype(int)
        df['is_month_end'] = (df['date'].dt.day >= 25).astype(int)
        
        # Drop rows with NaN in critical lag features
        df = df.dropna(subset=['lag_spending_1', 'lag_spending_2']).reset_index(drop=True)
        
        return df
    
    def preprocess_data(self, df):
        """Handle missing values and prepare features"""
        target = 'total_spending'
        feature_cols = [col for col in df.columns if col not in ['date', target]]
        
        X = df[feature_cols]
        y = df[target]
        
        # Handle missing values
        self.imputer = SimpleImputer(strategy='mean')
        X_imputed = pd.DataFrame(self.imputer.fit_transform(X), columns=X.columns)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = pd.DataFrame(self.scaler.fit_transform(X_imputed), columns=X.columns)
        
        self.features = feature_cols
        return X_scaled, y
    
    def train_model(self, X, y):
        """Train Random Forest model with better parameters"""
        if len(X) < 10:
            st.warning("⚠️ Not enough data for reliable predictions (need at least 10 data points)")
            return None
            
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False  # Don't shuffle time series
        )
        
        # Use better hyperparameters
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2': r2,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def generate_future_features(self, last_data, n_periods=6):
        """Generate features for future predictions"""
        future_data = []
        last_date = last_data['date'].iloc[-1]
        last_spending_values = last_data['total_spending'].tail(3).values
        
        for i in range(1, n_periods + 1):
            future_date = last_date + timedelta(days=30*i)  # Monthly predictions
            
            # Create feature row
            feature_row = {
                'year': future_date.year,
                'month': future_date.month,
                'day_of_year': future_date.timetuple().tm_yday,
                'day_of_week': future_date.weekday(),
                'is_weekend': int(future_date.weekday() in [5, 6]),
                'day_of_month': future_date.day,
                'quarter': (future_date.month - 1) // 3 + 1,
                'is_month_start': int(future_date.day <= 5),
                'is_month_end': int(future_date.day >= 25)
            }
            
            # Add lag features - use recent actual values or previous predictions
            if i == 1:
                feature_row['lag_spending_1'] = last_spending_values[-1]
                feature_row['lag_spending_2'] = last_spending_values[-2] if len(last_spending_values) > 1 else last_spending_values[-1]
                feature_row['lag_spending_3'] = last_spending_values[-3] if len(last_spending_values) > 2 else last_spending_values[-1]
            else:
                # Use previous predictions for lag features
                prev_predictions = [row.get('predicted_spending', last_spending_values[-1]) for row in future_data]
                feature_row['lag_spending_1'] = prev_predictions[-1] if prev_predictions else last_spending_values[-1]
                feature_row['lag_spending_2'] = prev_predictions[-2] if len(prev_predictions) > 1 else last_spending_values[-1]
                feature_row['lag_spending_3'] = prev_predictions[-3] if len(prev_predictions) > 2 else last_spending_values[-1]
            
            # Add rolling averages (use recent actual data)
            feature_row['rolling_avg_7'] = last_data['total_spending'].tail(7).mean()
            feature_row['rolling_avg_30'] = last_data['total_spending'].tail(30).mean()
            
            # Add other features from recent data
            for col in self.features:
                if col not in feature_row:
                    feature_row[col] = last_data[col].tail(3).mean()
            
            feature_row['date'] = future_date
            future_data.append(feature_row)
        
        return pd.DataFrame(future_data)
    
    def predict_future_spending(self, df, n_months=6):
        """Predict future spending"""
        if self.model is None:
            st.error("❌ Model not trained")
            return None
            
        # Generate future features
        future_df = self.generate_future_features(df, n_months)
        
        # Prepare features for prediction
        X_future = future_df[self.features]
        X_future_imputed = pd.DataFrame(self.imputer.transform(X_future), columns=X_future.columns)
        X_future_scaled = pd.DataFrame(self.scaler.transform(X_future_imputed), columns=X_future.columns)
        
        # Make predictions
        predictions = self.model.predict(X_future_scaled)
        
        # Add predictions to dataframe
        future_df['predicted_spending'] = predictions
        
        # Update lag features with predictions for better accuracy
        for i in range(len(future_df)):
            if i > 0:
                future_df.iloc[i]['predicted_spending'] = predictions[i]
        
        return future_df[['date', 'predicted_spending']]

def render_prediction_tab(analyzer, processor, db_connection, start_date, end_date):
    """Render the spending prediction tab"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2>🔮 Spending Predictions</h2>
        <p>AI-powered forecasting of your future spending patterns</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize predictor
    predictor = SpendingPredictor(analyzer, db_connection)
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ⚙️ Prediction Settings")
        
        n_months = st.slider(
            "Prediction Period (months)",
            min_value=1,
            max_value=12,
            value=6,
            help="Number of months to predict into the future"
        )
        
        retrain_model = st.button(
            "🔄 Retrain Model",
            help="Retrain the prediction model with latest data"
        )
    
    with col1:
        # Load and process data
        with st.spinner("📊 Loading financial data..."):
            df = predictor.load_data()
        
        if df is None or df.empty:
            st.error("❌ No data available for predictions")
            return
        
        # Show data info
        st.info(f"📈 Loaded {len(df)} days of transaction data from {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        
        # Engineer features
        with st.spinner("🔧 Engineering features..."):
            df_featured = predictor.engineer_features(df)
        
        if df_featured.empty:
            st.error("❌ Not enough data for feature engineering")
            return
        
        # Train model
        with st.spinner("🤖 Training prediction model..."):
            X, y = predictor.preprocess_data(df_featured)
            metrics = predictor.train_model(X, y)
        
        if metrics is None:
            return
        
        # Show model performance
        st.success(f"✅ Model trained successfully!")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        with perf_col1:
            st.metric("R² Score", f"{metrics['r2']:.3f}")
        with perf_col2:
            st.metric("RMSE", f"R{metrics['rmse']:.0f}")
        with perf_col3:
            st.metric("Training Size", f"{metrics['train_size']} days")
    
    # Generate predictions
    with st.spinner("🔮 Generating predictions..."):
        predictions_df = predictor.predict_future_spending(df_featured, n_months)
    
    if predictions_df is None:
        return
    
    # Display predictions
    st.markdown("### 📊 Prediction Results")
    
    # Create visualization
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Historical vs Predicted Spending', 'Monthly Prediction Breakdown'),
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3]
    )
    
    # Historical data
    recent_data = df_featured.tail(90)  # Last 90 days
    fig.add_trace(
        go.Scatter(
            x=recent_data['date'],
            y=recent_data['total_spending'],
            mode='lines+markers',
            name='Historical Spending',
            line=dict(color='#1f77b4'),
            marker=dict(size=4)
        ),
        row=1, col=1
    )
    
    # Predictions
    fig.add_trace(
        go.Scatter(
            x=predictions_df['date'],
            y=predictions_df['predicted_spending'],
            mode='lines+markers',
            name='Predicted Spending',
            line=dict(color='#ff7f0e', dash='dash'),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Monthly breakdown
    fig.add_trace(
        go.Bar(
            x=predictions_df['date'].dt.strftime('%Y-%m'),
            y=predictions_df['predicted_spending'],
            name='Monthly Predictions',
            marker_color='#ff7f0e',
            opacity=0.7
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Spending Prediction Analysis",
        title_x=0.5
    )
    
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Spending (R)", row=1, col=1)
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_yaxes(title_text="Predicted Spending (R)", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Prediction summary table
    st.markdown("### 📋 Detailed Predictions")
    
    # Format predictions for display
    display_df = predictions_df.copy()
    display_df['Month'] = display_df['date'].dt.strftime('%B %Y')
    display_df['Predicted Spending'] = display_df['predicted_spending'].apply(lambda x: f"R{x:,.0f}")
    display_df['Date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        display_df[['Month', 'Date', 'Predicted Spending']],
        use_container_width=True,
        hide_index=True
    )
    
    # Summary insights
    st.markdown("### 💡 Insights")
    
    total_predicted = predictions_df['predicted_spending'].sum()
    avg_monthly = predictions_df['predicted_spending'].mean()
    trend = "increasing" if predictions_df['predicted_spending'].iloc[-1] > predictions_df['predicted_spending'].iloc[0] else "decreasing"
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.metric(
            "Total Predicted Spending",
            f"R{total_predicted:,.0f}",
            help=f"Sum of all predictions for the next {n_months} months"
        )
    
    with insight_col2:
        st.metric(
            "Average Monthly Spending",
            f"R{avg_monthly:,.0f}",
            help="Average predicted monthly spending"
        )
    
    with insight_col3:
        st.metric(
            "Spending Trend",
            trend.title(),
            help="General direction of spending predictions"
        )
    
    # Download predictions
    st.markdown("### 💾 Export Predictions")
    
    csv = predictions_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Predictions as CSV",
        data=csv,
        file_name=f"spending_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )