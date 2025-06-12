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

class TransactionCategorizer:
    """Advanced ML-based transaction categorizer with integration support"""
    
    def __init__(self, model_dir="models"):
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
        
    def preprocess_description(self, description):
        """Enhanced text preprocessing for transaction descriptions"""
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
    
    def extract_features(self, descriptions):
        """Extract and engineer features from transaction descriptions"""
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
    
    def prepare_training_data(self, df):
        """Prepare training data from transaction DataFrame"""
        # Filter out uncategorized transactions for training
        training_df = df[df['category'] != 'Uncategorized'].copy()
        
        if len(training_df) < 10:
            raise ValueError("Need at least 10 categorized transactions for training")
        
        # Extract features
        X = self.extract_features(training_df['description'])
        
        # Encode labels
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(training_df['category'])
        else:
            y = self.label_encoder.transform(training_df['category'])
        
        return X, y, training_df
    
    def build_model(self, input_dim, num_classes):
        """Build an enhanced neural network model"""
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
    
    def train(self, df, validation_split=0.2, epochs=100, batch_size=32):
        """Train the categorization model"""
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
    
    def predict_single(self, description, return_confidence=False):
        """Predict category for a single transaction description"""
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
    
    def predict_batch(self, descriptions, confidence_threshold=0.5):
        """Predict categories for multiple descriptions"""
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
            
            return final_categories.tolist(), confidences.tolist()
            
        except Exception as e:
            self.logger.error(f"Batch prediction failed: {str(e)}")
            return ['Uncategorized'] * len(descriptions), [0.0] * len(descriptions)
    
    def save_model(self):
        """Save the trained model and preprocessors"""
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
    
    def load_model(self):
        """Load existing trained model and preprocessors"""
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
    
    def get_model_info(self):
        """Get information about the current model"""
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
    
    def auto_categorize_dataframe(self, df, confidence_threshold=0.7):
        """Automatically categorize uncategorized transactions in a DataFrame"""
        if not self.is_trained:
            self.logger.warning("Model not trained. Cannot auto-categorize.")
            return df
        
        # Find uncategorized transactions
        uncategorized_mask = (df['category'] == 'Uncategorized') | df['category'].isna()
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
        result_df.loc[uncategorized_mask, 'category'] = categories
        result_df.loc[uncategorized_mask, 'confidence'] = confidences
        
        # Log results
        categorized_count = sum(1 for cat in categories if cat != 'Uncategorized')
        self.logger.info(f"Successfully categorized {categorized_count} out of {len(uncategorized_df)} transactions")
        
        return result_df