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
from utils.utils import debug_write
warnings.filterwarnings('ignore')

class SpendingPredictor:
    def __init__(self, analyzer, processor, db_connection):
        self.analyzer = analyzer
        self.processor = processor
        self.db_connection = db_connection
        self.model = None
        self.scaler = None
        self.imputer = None
        self.features = []
        
    def load_data(self, start_date, end_date, data_source="Auto"):
        """Load transaction data using the same pattern as key_metrics_tab"""
        transactions_df = pd.DataFrame()
        data_info = {}
        
        # Determine data source availability
        local_available = self.processor.get_statement_info() is not None
        debug_write(f"Local data available: {local_available}")
        
        db_available = False
        try:
            doc_count = self.db_connection.count_documents()
            db_available = doc_count > 0
            debug_write(f"Database documents count: {doc_count}")
        except Exception as e:
            debug_write(f"ERROR: Database check failed: {str(e)}")
        
        # Auto-select data source if not specified
        if data_source == "Auto":
            if db_available:
                data_source = "Database Query"
            elif local_available:
                data_source = "Local File"
            else:
                st.error("❌ No data available from any source")
                return None, {}
        
        # Load from Database
        if data_source == "Database Query" and db_available:
            try:
                st.info(f"🔍 Querying database for transactions between {start_date} and {end_date}")
                with st.spinner("Loading data from database..."):
                    query = {
                        "$or": [
                            {
                                "period.start": {"$lte": end_date.strftime("%Y-%m-%d")},
                                "period.end": {"$gte": start_date.strftime("%Y-%m-%d")}
                            },
                            {
                                "period.start": {"$exists": False}
                            }
                        ]
                    }
                    documents = self.db_connection.find_documents(query=query, sort_by=[("uploaded_at", -1)])
                    debug_write(f"Found {len(documents)} document(s) in database")
                    
                    if documents:
                        for doc in documents:
                            debug_write(f"Processing document with keys: {list(doc.keys())}")
                            df = self.processor.process_latest_json()
                            if not df.empty:
                                # Standardize column names
                                df = self._standardize_columns(df)
                                
                                # Filter by date
                                if 'date' in df.columns:
                                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                                    df = df[
                                        (df['date'] >= pd.to_datetime(start_date)) &
                                        (df['date'] <= pd.to_datetime(end_date))
                                    ]
                                
                                if not df.empty:
                                    transactions_df = pd.concat([transactions_df, df], ignore_index=True)
                    
                    if not transactions_df.empty:
                        transactions_df = transactions_df.drop_duplicates().sort_values('date')
                        data_info = {
                            'source': 'Database',
                            'documents_found': len(documents),
                            'transactions_loaded': len(transactions_df),
                            'date_range': f"{start_date} to {end_date}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"transactions_df shape: {transactions_df.shape}")
                    else:
                        st.warning(f"No transactions found in database for date range {start_date} to {end_date}")
                        if local_available:
                            data_source = "Local File"
            except Exception as e:
                st.error(f"Error querying database: {str(e)}")
                if local_available:
                    st.info("Falling back to local file...")
                    data_source = "Local File"
        
        # Load from Local File
        if (data_source == "Local File" and local_available) or (data_source == "Database Query" and transactions_df.empty and local_available):
            try:
                with st.spinner("Loading data from local file..."):
                    transactions_df = self.processor.load_latest_bank_statement()
                    statement_info = self.processor.get_statement_info()
                    debug_write(f"Statement info: {statement_info}")
                    
                    if not transactions_df.empty and statement_info:
                        # Standardize column names
                        transactions_df = self._standardize_columns(transactions_df)
                        
                        # Check date range overlap
                        period = statement_info.get('period', {})
                        if period.get('start') and period.get('end'):
                            file_start = pd.to_datetime(period['start'])
                            file_end = pd.to_datetime(period['end'])
                            selected_start = pd.to_datetime(start_date)
                            selected_end = pd.to_datetime(end_date)
                            
                            if file_end < selected_start or file_start > selected_end:
                                st.warning(f"⚠️ Local file covers {period['start']} to {period['end']}, but you selected {start_date} to {end_date}. There may be no overlapping data.")
                            
                            # Filter to selected date range
                            if 'date' in transactions_df.columns:
                                transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce')
                                original_count = len(transactions_df)
                                transactions_df = transactions_df[
                                    (transactions_df['date'] >= selected_start) &
                                    (transactions_df['date'] <= selected_end)
                                ]
                                filtered_count = len(transactions_df)
                                
                                if filtered_count == 0:
                                    st.warning(f"No transactions found in local file for your selected date range ({start_date} to {end_date})")
                                elif filtered_count < original_count:
                                    st.info(f"Filtered to {filtered_count} transactions (from {original_count} total) matching your date range")
                        
                        data_info = {
                            'source': 'Local File',
                            'filename': statement_info.get('filename', 'Unknown'),
                            'file_period': f"{period.get('start', 'Unknown')} to {period.get('end', 'Unknown')}",
                            'transactions_loaded': len(transactions_df),
                            'selected_range': f"{start_date} to {end_date}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"transactions_df shape: {transactions_df.shape}")
                    
            except Exception as e:
                st.error(f"Error loading local file: {str(e)}")
        
        # Return processed data
        if not transactions_df.empty:
            # Convert to daily aggregated format for predictions
            daily_df = self._aggregate_daily_data(transactions_df)
            return daily_df, data_info
        else:
            return None, data_info
    
    def _standardize_columns(self, df):
        """Standardize column names to match expected format"""
        column_mapping = {
            'Date': 'date',
            'Transaction Date': 'date',
            'Trans Date': 'date',
            'Description': 'description',
            'Details': 'description',
            'Trans Details': 'description',
            'Debit': 'debits',
            'Debits': 'debits',
            'Credit': 'credits',
            'Credits': 'credits',
            'Balance': 'balance',
            'Running Balance': 'balance',
            'Saldo': 'balance'
        }
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_columns = ['date', 'description', 'debits', 'credits', 'balance']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 'Unknown' if col == 'description' else 0.0
        
        return df
    
    def _aggregate_daily_data(self, df):
        """Aggregate transaction data by day for prediction"""
        if df.empty:
            return None
        
        # Ensure numeric columns
        df['debits'] = pd.to_numeric(df['debits'], errors='coerce').fillna(0)
        df['credits'] = pd.to_numeric(df['credits'], errors='coerce').fillna(0)
        
        # Calculate net spending
        df['net_spending'] = df['debits'] - df['credits']
        
        # Group by date
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
        min_required = max(5, len(X) // 4)  # Adaptive minimum
        if len(X) < min_required:
            st.warning(f"⚠️ Limited data ({len(X)} points). Predictions may be less reliable.")
        # if len(X) < 10:
        #     st.warning("⚠️ Not enough data for reliable predictions (need at least 10 data points)")
            return None
            
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False  # Don't shuffle time series
        )
        
        # Use better hyperparameters
        self.model = RandomForestRegressor(
            n_estimators=50,       # Reduced from 200
            max_depth=10,         # Reduced from 15
            min_samples_split=10, # Increased (simpler trees)
            min_samples_leaf=5,   # Increased (simpler trees)
            max_features='sqrt',  # Reduced feature subset
            random_state=42,
            n_jobs=2             # Limit CPU usage (2 cores) to avoid overloading
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
    predictor = SpendingPredictor(analyzer, processor, db_connection)
    
    # Check data availability
    local_available = processor.get_statement_info() is not None
    db_available = False
    try:
        doc_count = db_connection.count_documents()
        db_available = doc_count > 0
    except Exception:
        pass
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ⚙️ Prediction Settings")
        
        # Data source selection
        data_source_options = []
        if db_available:
            data_source_options.append("Database Query")
        if local_available:
            data_source_options.append("Local File")
        if not data_source_options:
            data_source_options = ["No Data"]
        
        data_source = st.selectbox(
            "Data Source:",
            data_source_options,
            help="Choose data source for predictions"
        )
        
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
        # Handle no data case
        if data_source == "No Data":
            st.error("❌ No data available for predictions. Please upload a bank statement in the 'Upload & Process' tab.")
            return
        
        # Load and process data
        with st.spinner("📊 Loading financial data..."):
            df, data_info = predictor.load_data(start_date, end_date, data_source)
        
        if df is None or df.empty:
            st.error("❌ No data available for predictions in the selected date range")
            return
        
        # Display data info
        if data_info:
            with st.expander("📋 Data Source Information", expanded=False):
                for key, value in data_info.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
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
