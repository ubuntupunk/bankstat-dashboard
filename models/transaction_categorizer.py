import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import re
import logging
from typing import List, Tuple, Dict, Any, Optional
import threading
import warnings

# Suppress TensorFlow warnings and configure memory growth
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')

# Try to import TensorFlow safely
try:
    import tensorflow as tf
    # Configure TensorFlow for better stability
    tf.config.experimental.set_memory_growth = True
    tf.get_logger().setLevel('ERROR')
    
    # Limit TensorFlow threads to prevent conflicts
    tf.config.threading.set_intra_op_parallelism_threads(1)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    
    # Set memory limit if GPU is available
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            logging.warning(f"GPU configuration failed: {e}")
    
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available, using scikit-learn models only")

class TransactionCategorizer:
    """Enhanced ML-based transaction categorizer with fallback models and stability fixes"""
    
    def __init__(self, model_dir: str = "models", use_tensorflow: bool = True):
        """
        Initializes the TransactionCategorizer with fallback options.
        
        Args:
            model_dir (str): Directory to store and load ML models.
            use_tensorflow (bool): Whether to use TensorFlow models (with fallback to sklearn).
        """
        self.model_dir = model_dir
        self.use_tensorflow = use_tensorflow and TENSORFLOW_AVAILABLE
        
        # Model paths
        self.tf_model_path = os.path.join(model_dir, "transaction_model.h5")
        self.sklearn_model_path = os.path.join(model_dir, "sklearn_model.pkl")
        self.vectorizer_path = os.path.join(model_dir, "vectorizer.pkl")
        self.encoder_path = os.path.join(model_dir, "label_encoder.pkl")
        
        # Create model directory
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize components
        self.tf_model = None
        self.sklearn_model = None
        self.vectorizer = None
        self.label_encoder = None
        self.is_trained = False
        self.model_type = 'sklearn'  # 'tensorflow' or 'sklearn'
        
        # Thread lock for thread safety
        self._lock = threading.Lock()
        
        # Load existing model if available
        self.load_model()
        
        # Enhanced preprocessing patterns
        self.preprocessing_patterns = {
            'remove_numbers': r'\d+',
            'remove_special': r'[^\w\s]',
            'common_words': ['debit', 'credit', 'card', 'payment', 'purchase', 'transaction'],
            'merchant_indicators': ['ltd', 'inc', 'corp', 'co', 'pty', 'llc']
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def preprocess_description(self, description: str) -> str:
        """
        Enhanced text preprocessing for transaction descriptions.
        
        Args:
            description (str): The raw transaction description.
            
        Returns:
            str: The cleaned and preprocessed description.
        """
        if pd.isna(description) or not isinstance(description, str):
            return ""
        
        # Convert to lowercase
        text = description.lower().strip()
        
        # Remove common banking terms that don't help categorization
        banking_terms = ['pos', 'atm', 'eft', 'internet', 'online', 'mobile', 'card', 'purchase']
        for term in banking_terms:
            text = re.sub(rf'\b{term}\b', '', text)
        
        # Extract merchant name (usually at the beginning)
        # Remove transaction codes and reference numbers
        text = re.sub(r'\b\d{6,}\b', '', text)  # Remove long numbers
        text = re.sub(r'\b[a-z0-9]{8,}\b', '', text)  # Remove reference codes
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove special characters
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_features(self, descriptions: List[str]) -> np.ndarray:
        """
        Extract and engineer features from transaction descriptions.
        
        Args:
            descriptions (List[str]): A list of transaction descriptions.
            
        Returns:
            np.ndarray: TF-IDF features as a NumPy array.
        """
        try:
            processed_descriptions = [self.preprocess_description(desc) for desc in descriptions]
            
            # Create TF-IDF features
            if self.vectorizer is None:
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,  # Reduced for stability
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    stop_words='english'
                )
                tfidf_features = self.vectorizer.fit_transform(processed_descriptions)
            else:
                tfidf_features = self.vectorizer.transform(processed_descriptions)
            
            return tfidf_features.toarray()
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}")
            # Return zero features as fallback
            return np.zeros((len(descriptions), 100))
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Prepare training data from transaction DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing transaction data.
            
        Returns:
            Tuple[np.ndarray, np.ndarray, pd.DataFrame]: Features (X), labels (y), and filtered DataFrame.
        """
        # Ensure required columns exist
        if 'description' not in df.columns:
            raise ValueError("DataFrame must contain 'description' column")
        
        if 'category_name' not in df.columns:
            df['category_name'] = 'Uncategorized'
        
        # Filter out uncategorized transactions for training
        training_df = df[
            (df['category_name'] != 'Uncategorized') & 
            (df['category_name'].notna()) &
            (df['category_name'] != '')
        ].copy()
        
        if len(training_df) < 10:
            raise ValueError("Need at least 10 categorized transactions for training")
        
        # Extract features
        X = self.extract_features(training_df['description'].tolist())
        
        # Encode labels
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(training_df['category_name'])
        else:
            # Handle new categories
            known_categories = set(self.label_encoder.classes_)
            new_categories = set(training_df['category_name'].unique()) - known_categories
            
            if new_categories:
                # Refit encoder with all categories
                all_categories = list(known_categories) + list(new_categories)
                self.label_encoder = LabelEncoder()
                self.label_encoder.fit(all_categories)
            
            y = self.label_encoder.transform(training_df['category_name'])
        
        return X, y, training_df
    
    def build_tensorflow_model(self, input_dim: int, num_classes: int):
        """
        Build a TensorFlow model with safety measures.
        
        Args:
            input_dim (int): Dimension of input features.
            num_classes (int): Number of output classes.
            
        Returns:
            tf.keras.Model: Compiled TensorFlow model.
        """
        if not TENSORFLOW_AVAILABLE:
            raise RuntimeError("TensorFlow not available")
        
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
            from tensorflow.keras.regularizers import l2
            
            # Clear any existing sessions
            tf.keras.backend.clear_session()
            
            model = Sequential([
                Dense(128, activation='relu', input_shape=(input_dim,), 
                      kernel_regularizer=l2(0.001)),
                BatchNormalization(),
                Dropout(0.3),
                
                Dense(64, activation='relu', kernel_regularizer=l2(0.001)),
                BatchNormalization(),
                Dropout(0.3),
                
                Dense(32, activation='relu', kernel_regularizer=l2(0.001)),
                Dropout(0.2),
                
                Dense(num_classes, activation='softmax')
            ])
            
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            return model
            
        except Exception as e:
            self.logger.error(f"TensorFlow model creation failed: {str(e)}")
            raise e
    
    def build_sklearn_model(self, num_classes: int):
        """
        Build a scikit-learn model as fallback.
        
        Args:
            num_classes (int): Number of output classes.
            
        Returns:
            sklearn model: Compiled scikit-learn model.
        """
        try:
            if num_classes > 10:
                # Use Random Forest for many categories
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=1  # Single thread for stability
                )
            else:
                # Use Logistic Regression for fewer categories
                model = LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                    multi_class='ovr'
                )
            
            return model
            
        except Exception as e:
            self.logger.error(f"Sklearn model creation failed: {str(e)}")
            raise e
    
    def train(self, df: pd.DataFrame, validation_split: float = 0.2, 
              epochs: int = 50, batch_size: int = 32) -> Dict[str, Any]:
        """
        Train the categorization model with fallback options.
        
        Args:
            df (pd.DataFrame): DataFrame containing transaction data.
            validation_split (float): Proportion of data for validation.
            epochs (int): Number of training epochs (TensorFlow only).
            batch_size (int): Batch size (TensorFlow only).
            
        Returns:
            Dict[str, Any]: Training results.
        """
        with self._lock:
            try:
                # Prepare data
                X, y, training_df = self.prepare_training_data(df)
                num_classes = len(np.unique(y))
                
                self.logger.info(f"Training with {len(X)} samples across {num_classes} categories")
                
                # Split data
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=validation_split, random_state=42, 
                    stratify=y if len(np.unique(y)) > 1 else None
                )
                
                # Try TensorFlow first if available and requested
                if self.use_tensorflow and TENSORFLOW_AVAILABLE:
                    try:
                        self.logger.info("Training with TensorFlow model...")
                        return self._train_tensorflow(X_train, X_val, y_train, y_val, 
                                                    epochs, batch_size, num_classes)
                    except Exception as tf_error:
                        self.logger.warning(f"TensorFlow training failed: {tf_error}")
                        self.logger.info("Falling back to scikit-learn model...")
                
                # Fallback to scikit-learn
                return self._train_sklearn(X_train, X_val, y_train, y_val, num_classes)
                
            except Exception as e:
                self.logger.error(f"Training failed: {str(e)}")
                raise e
    
    def _train_tensorflow(self, X_train, X_val, y_train, y_val, epochs, batch_size, num_classes):
        """Train TensorFlow model with error handling."""
        try:
            from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
            
            self.tf_model = self.build_tensorflow_model(X_train.shape[1], num_classes)
            
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True, 
                            monitor='val_accuracy', verbose=0),
                ReduceLROnPlateau(factor=0.5, patience=5, min_lr=0.0001, verbose=0)
            ]
            
            # Train with reduced verbosity
            history = self.tf_model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=0  # Reduced verbosity
            )
            
            # Evaluate
            val_predictions = self.tf_model.predict(X_val, verbose=0)
            val_pred_classes = np.argmax(val_predictions, axis=1)
            
            report = classification_report(
                y_val, val_pred_classes,
                target_names=self.label_encoder.classes_,
                output_dict=True,
                zero_division=0
            )
            
            self.model_type = 'tensorflow'
            self.is_trained = True
            self.save_model()
            
            self.logger.info(f"TensorFlow training completed. Accuracy: {report['accuracy']:.3f}")
            
            return {
                'model_type': 'tensorflow',
                'history': history,
                'classification_report': report,
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'categories': list(self.label_encoder.classes_)
            }
            
        except Exception as e:
            self.logger.error(f"TensorFlow training error: {str(e)}")
            # Clean up any partial TensorFlow model
            self.tf_model = None
            tf.keras.backend.clear_session()
            raise e
    
    def _train_sklearn(self, X_train, X_val, y_train, y_val, num_classes):
        """Train scikit-learn model."""
        try:
            self.sklearn_model = self.build_sklearn_model(num_classes)
            
            # Train model
            self.sklearn_model.fit(X_train, y_train)
            
            # Evaluate
            val_predictions = self.sklearn_model.predict(X_val)
            
            report = classification_report(
                y_val, val_predictions,
                target_names=self.label_encoder.classes_,
                output_dict=True,
                zero_division=0
            )
            
            self.model_type = 'sklearn'
            self.is_trained = True
            self.save_model()
            
            self.logger.info(f"Scikit-learn training completed. Accuracy: {report['accuracy']:.3f}")
            
            return {
                'model_type': 'sklearn',
                'classification_report': report,
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'categories': list(self.label_encoder.classes_)
            }
            
        except Exception as e:
            self.logger.error(f"Scikit-learn training error: {str(e)}")
            raise e
    
    def predict_single(self, description: str, return_confidence: bool = False):
        """
        Predict category for a single transaction description.
        
        Args:
            description (str): Transaction description.
            return_confidence (bool): Whether to return confidence.
            
        Returns:
            str or Tuple[str, float]: Predicted category and optionally confidence.
        """
        if not self.is_trained:
            return 'Uncategorized' if not return_confidence else ('Uncategorized', 0.0)
        
        try:
            with self._lock:
                X = self.extract_features([description])
                
                if self.model_type == 'tensorflow' and self.tf_model:
                    prediction = self.tf_model.predict(X, verbose=0)
                    predicted_class = np.argmax(prediction[0])
                    confidence = float(np.max(prediction[0]))
                    
                elif self.model_type == 'sklearn' and self.sklearn_model:
                    prediction = self.sklearn_model.predict(X)
                    predicted_class = prediction[0]
                    
                    # Get confidence from predict_proba if available
                    if hasattr(self.sklearn_model, 'predict_proba'):
                        proba = self.sklearn_model.predict_proba(X)
                        confidence = float(np.max(proba[0]))
                    else:
                        confidence = 0.8  # Default confidence for models without probability
                
                else:
                    return 'Uncategorized' if not return_confidence else ('Uncategorized', 0.0)
                
                category = self.label_encoder.inverse_transform([predicted_class])[0]
                
                if return_confidence:
                    return category, confidence
                return category
                
        except Exception as e:
            self.logger.error(f"Prediction failed for '{description}': {str(e)}")
            return 'Uncategorized' if not return_confidence else ('Uncategorized', 0.0)
    
    def predict_batch(self, descriptions: List[str], confidence_threshold: float = 0.5) -> Tuple[List[str], List[float]]:
        """
        Predict categories for multiple descriptions.
        
        Args:
            descriptions (List[str]): Transaction descriptions.
            confidence_threshold (float): Minimum confidence threshold.
            
        Returns:
            Tuple[List[str], List[float]]: Category names and confidences.
        """
        if not self.is_trained:
            return ['Uncategorized'] * len(descriptions), [0.0] * len(descriptions)
        
        try:
            with self._lock:
                X = self.extract_features(descriptions)
                
                if self.model_type == 'tensorflow' and self.tf_model:
                    predictions = self.tf_model.predict(X, verbose=0)
                    predicted_classes = np.argmax(predictions, axis=1)
                    confidences = np.max(predictions, axis=1)
                    
                elif self.model_type == 'sklearn' and self.sklearn_model:
                    predicted_classes = self.sklearn_model.predict(X)
                    
                    if hasattr(self.sklearn_model, 'predict_proba'):
                        probabilities = self.sklearn_model.predict_proba(X)
                        confidences = np.max(probabilities, axis=1)
                    else:
                        confidences = np.full(len(descriptions), 0.8)
                
                else:
                    return ['Uncategorized'] * len(descriptions), [0.0] * len(descriptions)
                
                # Convert to category names
                categories = self.label_encoder.inverse_transform(predicted_classes)
                
                # Apply confidence threshold
                final_categories = []
                for category, confidence in zip(categories, confidences):
                    if confidence >= confidence_threshold:
                        final_categories.append(category)
                    else:
                        final_categories.append('Uncategorized')
                
                return final_categories, confidences.tolist()
                
        except Exception as e:
            self.logger.error(f"Batch prediction failed: {str(e)}")
            return ['Uncategorized'] * len(descriptions), [0.0] * len(descriptions)
    
    def save_model(self) -> bool:
        """Save the trained model and preprocessors."""
        try:
            # Save TensorFlow model
            if self.model_type == 'tensorflow' and self.tf_model:
                self.tf_model.save(self.tf_model_path)
            
            # Save scikit-learn model
            if self.model_type == 'sklearn' and self.sklearn_model:
                with open(self.sklearn_model_path, 'wb') as f:
                    pickle.dump(self.sklearn_model, f)
            
            # Save preprocessors
            if self.vectorizer:
                with open(self.vectorizer_path, 'wb') as f:
                    pickle.dump(self.vectorizer, f)
            
            if self.label_encoder:
                with open(self.encoder_path, 'wb') as f:
                    pickle.dump(self.label_encoder, f)
            
            self.logger.info(f"Model saved successfully (type: {self.model_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def load_model(self) -> bool:
        """Load existing trained model and preprocessors."""
        try:
            model_loaded = False
            
            # Try to load TensorFlow model first
            if self.use_tensorflow and TENSORFLOW_AVAILABLE and os.path.exists(self.tf_model_path):
                try:
                    from tensorflow.keras.models import load_model
                    self.tf_model = load_model(self.tf_model_path)
                    self.model_type = 'tensorflow'
                    model_loaded = True
                    self.logger.info("TensorFlow model loaded successfully")
                except Exception as e:
                    self.logger.warning(f"Failed to load TensorFlow model: {e}")
            
            # Try to load scikit-learn model
            if not model_loaded and os.path.exists(self.sklearn_model_path):
                try:
                    with open(self.sklearn_model_path, 'rb') as f:
                        self.sklearn_model = pickle.load(f)
                    self.model_type = 'sklearn'
                    model_loaded = True
                    self.logger.info("Scikit-learn model loaded successfully")
                except Exception as e:
                    self.logger.warning(f"Failed to load scikit-learn model: {e}")
            
            # Load preprocessors
            if os.path.exists(self.vectorizer_path):
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            
            if os.path.exists(self.encoder_path):
                with open(self.encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
            
            # Check if model is fully loaded
            if model_loaded and self.vectorizer and self.label_encoder:
                self.is_trained = True
                self.logger.info(f"Complete model loaded successfully (type: {self.model_type})")
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            self.is_trained = False
        
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            if not self.is_trained:
                return {"status": "Not trained"}
            
            info = {
                "status": "Trained",
                "model_type": self.model_type,
                "categories": list(self.label_encoder.classes_) if self.label_encoder else [],
                "vocab_size": len(self.vectorizer.vocabulary_) if self.vectorizer else 0,
            }
            
            # Add model-specific info
            if self.model_type == 'tensorflow' and self.tf_model:
                info["model_params"] = self.tf_model.count_params()
                if os.path.exists(self.tf_model_path):
                    info["last_modified"] = datetime.fromtimestamp(
                        os.path.getmtime(self.tf_model_path)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    
            elif self.model_type == 'sklearn':
                if os.path.exists(self.sklearn_model_path):
                    info["last_modified"] = datetime.fromtimestamp(
                        os.path.getmtime(self.sklearn_model_path)
                    ).strftime("%Y-%m-%d %H:%M:%S")
            
            return info
            
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def auto_categorize_dataframe(self, df: pd.DataFrame, confidence_threshold: float = 0.7) -> pd.DataFrame:
        """
        Automatically categorize uncategorized transactions in a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with transactions.
            confidence_threshold (float): Minimum confidence threshold.
            
        Returns:
            pd.DataFrame: Updated DataFrame with auto-categorized transactions.
        """
        if not self.is_trained:
            self.logger.warning("Model not trained. Cannot auto-categorize.")
            return df
        
        try:
            # Ensure required columns exist
            if 'category_name' not in df.columns:
                df['category_name'] = 'Uncategorized'
            
            # Find uncategorized transactions
            uncategorized_mask = (
                (df['category_name'] == 'Uncategorized') | 
                df['category_name'].isna() | 
                (df['category_name'] == '')
            )
            uncategorized_df = df[uncategorized_mask].copy()
            
            if len(uncategorized_df) == 0:
                return df
            
            self.logger.info(f"Auto-categorizing {len(uncategorized_df)} transactions")
            
            # Predict categories
            categories, confidences = self.predict_batch(
                uncategorized_df['description'].tolist(),
                confidence_threshold=confidence_threshold
            )
            
            # Update the dataframe
            result_df = df.copy()
            result_df.loc[uncategorized_mask, 'category_name'] = categories
            result_df.loc[uncategorized_mask, 'confidence'] = confidences
            
            # Log results
            categorized_count = sum(1 for cat in categories if cat != 'Uncategorized')
            self.logger.info(f"Successfully categorized {categorized_count} out of {len(uncategorized_df)} transactions")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"Auto-categorization failed: {str(e)}")
            return df
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            if TENSORFLOW_AVAILABLE:
                tf.keras.backend.clear_session()
        except:
            pass