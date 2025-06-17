import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.regularizers import l2
import re
import logging
from typing import List, Tuple, Dict, Any
from db.model import Category
from sqlalchemy.orm import Session
from db.connection import get_db_session # Assuming this exists for session management

class TransactionCategorizer:
    """Advanced ML-based transaction categorizer with integration support"""
    
    def __init__(self, model_dir: str = "models"):
        """
        Initializes the TransactionCategorizer.
        
        Args:
            model_dir (str): Directory to store and load ML models.
        """
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "transaction_model.h5")
        self.vectorizer_path = os.path.join(model_dir, "vectorizer.pkl")
        self.encoder_path = os.path.join(model_dir, "label_encoder.pkl")
        self.feature_names_path = os.path.join(model_dir, "feature_names.pkl")
        
        # Create model directory
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize components
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.feature_names = None
        self.is_trained = False
        
        # Load existing model if available
        self.load_model()
        
        # Enhanced preprocessing patterns
        self.preprocessing_patterns = {
            'remove_numbers': r'\d+',
            'remove_special': r'[^\w\s]',
            'common_words': ['debit', 'credit', 'card', 'payment', 'purchase', 'transaction'],
            'merchant_indicators': ['ltd', 'inc', 'corp', 'co', 'pty', 'llc']
        }
        
        logging.basicConfig(level=logging.INFO)
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
        banking_terms = ['pos', 'atm', 'eft', 'internet', 'online', 'mobile', 'card']
        for term in banking_terms:
            text = re.sub(rf'\b{term}\b', '', text)
        
        # Extract merchant name (usually at the beginning)
        # Remove transaction codes and reference numbers
        text = re.sub(r'\b\d{6,}\b', '', text)  # Remove long numbers
        text = re.sub(r'\b[a-z0-9]{8,}\b', '', text)  # Remove reference codes
        
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
        processed_descriptions = [self.preprocess_description(desc) for desc in descriptions]
        
        # Create TF-IDF features
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=2000,
                ngram_range=(1, 2),  # Include bigrams
                min_df=2,  # Ignore terms that appear in less than 2 documents
                max_df=0.95,  # Ignore terms that appear in more than 95% of documents
                stop_words='english'
            )
            tfidf_features = self.vectorizer.fit_transform(processed_descriptions)
        else:
            tfidf_features = self.vectorizer.transform(processed_descriptions)
        
        return tfidf_features.toarray()
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Prepare training data from transaction DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing transaction data with 'description' and 'category_name' columns.
            
        Returns:
            Tuple[np.ndarray, np.ndarray, pd.DataFrame]: Features (X), labels (y), and the filtered training DataFrame.
        """
        # Filter out uncategorized transactions for training
        training_df = df[df['category_name'] != 'Uncategorized'].copy()
        
        if len(training_df) < 10:
            raise ValueError("Need at least 10 categorized transactions for training")
        
        # Extract features
        X = self.extract_features(training_df['description'])
        
        # Encode labels
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(training_df['category_name'])
        else:
            y = self.label_encoder.transform(training_df['category_name'])
        
        return X, y, training_df
    
    def build_model(self, input_dim: int, num_classes: int) -> Sequential:
        """
        Build an enhanced neural network model.
        
        Args:
            input_dim (int): Dimension of the input features.
            num_classes (int): Number of output classes (categories).
            
        Returns:
            Sequential: The compiled Keras Sequential model.
        """
        model = Sequential([
            # Input layer with batch normalization
            Dense(256, activation='relu', input_shape=(input_dim,), 
                  kernel_regularizer=l2(0.001)),
            BatchNormalization(),
            Dropout(0.3),
            
            # Hidden layers
            Dense(128, activation='relu', kernel_regularizer=l2(0.001)),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu', kernel_regularizer=l2(0.001)),
            BatchNormalization(),
            Dropout(0.2),
            
            # Output layer
            Dense(num_classes, activation='softmax')
        ])
        
        # Compile with adaptive learning rate
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, df: pd.DataFrame, validation_split: float = 0.2, epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """
        Train the categorization model.
        
        Args:
            df (pd.DataFrame): DataFrame containing transaction data with 'description' and 'category_name' columns.
            validation_split (float): Proportion of data to use for validation.
            epochs (int): Number of training epochs.
            batch_size (int): Batch size for training.
            
        Returns:
            Dict[str, Any]: Training results including history, classification report, and categories.
        """
        try:
            # Prepare data
            X, y, training_df = self.prepare_training_data(df)
            
            self.logger.info(f"Training with {len(X)} samples across {len(np.unique(y))} categories")
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42, stratify=y
            )
            
            # Build model
            self.model = self.build_model(X.shape[1], len(np.unique(y)))
            
            # Callbacks for better training
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True, monitor='val_accuracy'),
                ReduceLROnPlateau(factor=0.5, patience=5, min_lr=0.0001)
            ]
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            # Evaluate model
            val_predictions = self.model.predict(X_val)
            val_pred_classes = np.argmax(val_predictions, axis=1)
            
            # Classification report
            report = classification_report(
                y_val, val_pred_classes,
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
            
            self.logger.info(f"Training completed. Validation accuracy: {report['accuracy']:.3f}")
            
            # Save model
            self.save_model()
            self.is_trained = True
            
            return {
                'history': history,
                'classification_report': report,
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'categories': list(self.label_encoder.classes_)
            }
            
        except Exception as e:
            self.logger.error(f"Training failed: {str(e)}")
            raise e
    
    def predict_single(self, description: str, return_confidence: bool = False) -> Tuple[str, float] | str:
        """
        Predict category for a single transaction description.
        
        Args:
            description (str): The transaction description to categorize.
            return_confidence (bool): Whether to return the prediction confidence.
            
        Returns:
            Union[str, Tuple[str, float]]: Predicted category name, optionally with confidence.
        """
        if not self.is_trained:
            return 'Uncategorized' if not return_confidence else ('Uncategorized', 0.0)
        
        try:
            # Preprocess and extract features
            X = self.extract_features([description])
            
            # Make prediction
            prediction = self.model.predict(X, verbose=0)
            predicted_class = np.argmax(prediction[0])
            confidence = np.max(prediction[0])
            
            # Convert back to category name
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
            descriptions (List[str]): A list of transaction descriptions.
            confidence_threshold (float): Minimum confidence for a category to be assigned.
            
        Returns:
            Tuple[List[str], List[float]]: Lists of predicted category names and their confidences.
        """
        if not self.is_trained:
            return ['Uncategorized'] * len(descriptions), [0.0] * len(descriptions)
        
        try:
            # Extract features
            X = self.extract_features(descriptions)
            
            # Make predictions
            predictions = self.model.predict(X, verbose=0)
            predicted_classes = np.argmax(predictions, axis=1)
            confidences = np.max(predictions, axis=1)
            
            # Convert to category names
            categories = self.label_encoder.inverse_transform(predicted_classes)
            
            # Apply confidence threshold
            final_categories = []
            for i, (category, confidence) in enumerate(zip(categories, confidences)):
                if confidence >= confidence_threshold:
                    final_categories.append(category)
                else:
                    final_categories.append('Uncategorized')
            
            return final_categories, confidences.tolist()
            
        except Exception as e:
            self.logger.error(f"Batch prediction failed: {str(e)}")
            return ['Uncategorized'] * len(descriptions), [0.0] * len(descriptions)
    
    def save_model(self) -> bool:
        """
        Save the trained model and preprocessors.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if self.model:
                self.model.save(self.model_path)
            
            if self.vectorizer:
                with open(self.vectorizer_path, 'wb') as f:
                    pickle.dump(self.vectorizer, f)
            
            if self.label_encoder:
                with open(self.encoder_path, 'wb') as f:
                    pickle.dump(self.label_encoder, f)
            
            self.logger.info("Model saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def load_model(self) -> bool:
        """
        Load existing trained model and preprocessors.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                self.logger.info("Model loaded successfully")
            
            if os.path.exists(self.vectorizer_path):
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            
            if os.path.exists(self.encoder_path):
                with open(self.encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
            
            # Check if model is fully loaded
            if self.model and self.vectorizer and self.label_encoder:
                self.is_trained = True
                self.logger.info("Complete model loaded successfully")
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            self.is_trained = False
        
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dict[str, Any]: Dictionary containing model status and details.
        """
        if not self.is_trained:
            return {"status": "Not trained"}
        
        try:
            return {
                "status": "Trained",
                "categories": list(self.label_encoder.classes_) if self.label_encoder else [],
                "vocab_size": len(self.vectorizer.vocabulary_) if self.vectorizer else 0,
                "model_params": self.model.count_params() if self.model else 0,
                "last_modified": datetime.fromtimestamp(os.path.getmtime(self.model_path)).strftime("%Y-%m-%d %H:%M:%S") if os.path.exists(self.model_path) else "Unknown"
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def auto_categorize_dataframe(self, df: pd.DataFrame, confidence_threshold: float = 0.7) -> pd.DataFrame:
        """
        Automatically categorize uncategorized transactions in a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with transactions, including 'description' and 'category_name'.
            confidence_threshold (float): Minimum confidence for a category to be assigned.
            
        Returns:
            pd.DataFrame: Updated DataFrame with auto-categorized transactions.
        """
        if not self.is_trained:
            self.logger.warning("Model not trained. Cannot auto-categorize.")
            return df
        
        # Find uncategorized transactions (assuming 'Uncategorized' is the default name)
        uncategorized_mask = (df['category_name'] == 'Uncategorized') | df['category_name'].isna()
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
