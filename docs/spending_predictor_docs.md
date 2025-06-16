# Spending Predictor ML Model Documentation & Improvements

## Current Model Architecture

### Data Flow Pipeline
1. **Data Loading** → Raw transaction data from database/file
2. **Column Standardization** → Normalize column names across different bank formats
3. **Daily Aggregation** → Convert transactions to daily spending totals
4. **Feature Engineering** → Create temporal and lag features
5. **Preprocessing** → Handle missing values and scale features
6. **Model Training** → Random Forest Regressor
7. **Future Prediction** → Generate forecasts for next N months

### Feature Engineering Strategy

#### Temporal Features
- `year`, `month`, `day_of_year` - Seasonal patterns
- `day_of_week`, `is_weekend` - Weekly spending patterns
- `quarter`, `is_month_start`, `is_month_end` - Monthly cycles

#### Lag Features (Time Series)
- `lag_spending_1/2/3` - Previous 1-3 days spending
- `rolling_avg_7/30` - Moving averages for trend detection

#### Current Model: Random Forest Regressor
```python
RandomForestRegressor(
    n_estimators=200,      # 200 trees
    max_depth=15,         # Prevent overfitting
    min_samples_split=5,  # Minimum samples to split
    min_samples_leaf=2,   # Minimum samples per leaf
    random_state=42,
    n_jobs=-1            # Use all CPU cores
)
```

## Issues with Current Implementation

### 1. Data Sparsity Problem
- **Issue**: Requires ≥10 data points after lag feature creation
- **Root Cause**: Daily aggregation + lag features reduce dataset size
- **Impact**: Fails with short transaction histories

### 2. Feature Leakage Risk
- **Issue**: Using rolling averages that include future information
- **Impact**: Overly optimistic model performance

### 3. Scaling Issues for Cloud Deployment
- **Issue**: Random Forest with 200 trees is CPU/memory intensive
- **Impact**: Slow training/prediction on limited resources

### 4. Poor Time Series Handling
- **Issue**: Random Forest doesn't capture temporal dependencies well
- **Impact**: Missing important spending patterns

## Recommended Improvements

### 1. Address Data Sparsity

#### Option A: Reduce Minimum Data Requirements
```python
# Current
if len(X) < 10:
    return None

# Improved
min_required = max(5, len(X) // 4)  # Adaptive minimum
if len(X) < min_required:
    st.warning(f"Limited data ({len(X)} points). Predictions may be less reliable.")
    # Continue with simplified model
```

#### Option B: Weekly/Monthly Aggregation for Small Datasets
```python
def adaptive_aggregation(self, df):
    """Choose aggregation level based on data size"""
    daily_count = len(df.groupby(df['date'].dt.date))
    
    if daily_count < 10:
        # Use weekly aggregation
        return self._aggregate_weekly_data(df)
    elif daily_count < 30:
        # Use bi-weekly aggregation  
        return self._aggregate_biweekly_data(df)
    else:
        return self._aggregate_daily_data(df)
```

### 2. Lightweight Model Alternatives

#### Option A: Linear Models (Fastest)
```python
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures

# Much faster, good for limited data
model = Ridge(alpha=1.0)
# Or with polynomial features for non-linearity
poly_features = PolynomialFeatures(degree=2, interaction_only=True)
```

#### Option B: Gradient Boosting (Medium Speed)
```python
from sklearn.ensemble import GradientBoostingRegressor

# Faster than Random Forest, often better for time series
model = GradientBoostingRegressor(
    n_estimators=50,        # Reduced from 200
    max_depth=6,           # Reduced complexity
    learning_rate=0.1,
    subsample=0.8,         # Use subset of data
    random_state=42
)
```

#### Option C: Simplified Random Forest
```python
# Cloud-optimized Random Forest
model = RandomForestRegressor(
    n_estimators=50,       # Reduced from 200
    max_depth=10,         # Reduced from 15
    min_samples_split=10, # Increased (simpler trees)
    min_samples_leaf=5,   # Increased (simpler trees)
    max_features='sqrt',  # Reduced feature subset
    random_state=42,
    n_jobs=2             # Limit CPU usage
)
```

### 3. Improved Feature Engineering

#### Remove Feature Leakage
```python
def engineer_features_safe(self, df):
    """Feature engineering without leakage"""
    df = df.copy()
    
    # Temporal features (safe)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Lag features (safe)
    df['lag_spending_1'] = df['total_spending'].shift(1)
    df['lag_spending_7'] = df['total_spending'].shift(7)
    
    # Historical rolling averages (safe - only past data)
    df['rolling_avg_7'] = df['total_spending'].shift(1).rolling(window=7, min_periods=1).mean()
    df['rolling_avg_30'] = df['total_spending'].shift(1).rolling(window=30, min_periods=1).mean()
    
    return df.dropna(subset=['lag_spending_1'])
```

### 4. Model Selection Strategy

#### Adaptive Model Selection
```python
def select_optimal_model(self, data_size, cpu_limit=True):
    """Choose model based on data size and resources"""
    
    if data_size < 20:
        # Simple linear model for very small datasets
        return Ridge(alpha=1.0), "Linear Ridge"
    
    elif data_size < 100:
        # Gradient boosting for medium datasets
        return GradientBoostingRegressor(
            n_estimators=30,
            max_depth=4,
            learning_rate=0.2
        ), "Gradient Boosting"
    
    elif cpu_limit:
        # Simplified RF for cloud deployment
        return RandomForestRegressor(
            n_estimators=30,
            max_depth=8,
            max_features='sqrt',
            n_jobs=2
        ), "Light Random Forest"
    
    else:
        # Full RF for powerful machines
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            n_jobs=-1
        ), "Full Random Forest"
```

### 5. Memory Optimization

#### Efficient Data Handling
```python
def optimize_memory(self, df):
    """Reduce memory usage"""
    # Convert to appropriate dtypes
    df['year'] = df['year'].astype('int16')
    df['month'] = df['month'].astype('int8') 
    df['day_of_week'] = df['day_of_week'].astype('int8')
    df['is_weekend'] = df['is_weekend'].astype('bool')
    
    # Use float32 instead of float64
    float_cols = df.select_dtypes(include=['float64']).columns
    df[float_cols] = df[float_cols].astype('float32')
    
    return df
```

### 6. Validation Strategy

#### Time Series Cross-Validation
```python
from sklearn.model_selection import TimeSeriesSplit

def validate_model(self, X, y):
    """Proper time series validation"""
    tscv = TimeSeriesSplit(n_splits=3)
    scores = []
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        self.model.fit(X_train, y_train)
        score = self.model.score(X_test, y_test)
        scores.append(score)
    
    return np.mean(scores), np.std(scores)
```

## Cloud Deployment Recommendations

### Streamlit Cloud
- **CPU**: 1 vCPU, 800MB RAM limit
- **Model**: Linear Ridge or Light Gradient Boosting
- **Max Estimators**: 30-50

### Vercel
- **Serverless**: 10-second execution limit
- **Model**: Pre-trained model with cached predictions
- **Strategy**: Train periodically, serve cached results

### Cloudflare Workers
- **CPU**: 50ms CPU time limit  
- **Model**: Simple linear model only
- **Strategy**: Statistical methods vs ML

## Implementation Priority

### Phase 1: Quick Fixes
1. Lower minimum data requirement to 5 points
2. Add weekly aggregation fallback
3. Reduce Random Forest to 50 estimators

### Phase 2: Model Improvements  
1. Implement adaptive model selection
2. Add proper time series validation
3. Memory optimization

### Phase 3: Advanced Features
1. Online learning for model updates
2. Uncertainty quantification
3. Multiple prediction horizons

## Alternative Approach: Statistical Methods

For very limited data or resources, consider simple statistical forecasting:

```python
def simple_forecast(self, df, n_months=6):
    """Statistical forecast when ML isn't viable"""
    # Trend analysis
    recent_avg = df['total_spending'].tail(30).mean()
    overall_avg = df['total_spending'].mean()
    
    # Seasonal adjustment
    monthly_pattern = df.groupby(df['date'].dt.month)['total_spending'].mean()
    
    # Simple trend + seasonal forecast
    predictions = []
    for i in range(1, n_months + 1):
        future_month = ((datetime.now().month + i - 1) % 12) + 1
        seasonal_factor = monthly_pattern.get(future_month, 1.0) / overall_avg
        prediction = recent_avg * seasonal_factor
        predictions.append(prediction)
    
    return predictions
```

This approach requires minimal data and computational resources while still providing reasonable forecasts based on historical patterns.