# connection.py
import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from config import Config
import logging

class DatabaseConnection:
    """Handles MongoDB database connections and operations"""
    
    def __init__(self):
        self.config = Config()
        self.db_password = self.config.db_password
        self.mongodb_url = self.config.mongodb_url
        self.uri = f"mongodb+srv://ubuntupunk:{self.db_password}@{self.mongodb_url}"
        self._client = None
        self._db = None
        self._collection = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    @st.cache_resource
    def get_client(_self):
        """Get MongoDB client with caching"""
        try:
            if _self._client is None:
                _self._client = MongoClient(_self.uri, server_api=ServerApi('1'))
                # Test the connection
                _self._client.admin.command('ping')
                _self.logger.info("Successfully connected to MongoDB")
            return _self._client
        except Exception as e:
            _self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            st.error(f"Database connection failed: {str(e)}")
            return None
    
    def get_database(self, db_name: str = "bankstat"):
        """Get database instance"""
        try:
            client = self.get_client()
            if client is None:
                return None
            
            if self._db is None or self._db.name != db_name:
                self._db = client[db_name]
                self.logger.info(f"Connected to database: {db_name}")
            
            return self._db
        except Exception as e:
            self.logger.error(f"Failed to get database {db_name}: {str(e)}")
            return None
    
    def get_collection(self, collection_name: str = "statements", db_name: str = "bankstat"):
        """Get collection instance"""
        try:
            db = self.get_database(db_name)
            if db is None:
                return None
            
            if self._collection is None or self._collection.name != collection_name:
                self._collection = db[collection_name]
                self.logger.info(f"Connected to collection: {collection_name}")
            
            return self._collection
        except Exception as e:
            self.logger.error(f"Failed to get collection {collection_name}: {str(e)}")
            return None
    
    def test_connection(self):
        """Test database connection and return status"""
        try:
            client = self.get_client()
            if client is None:
                return False, "Failed to get client"
            
            # Ping the database
            client.admin.command('ping')
            
            # Test collection access
            collection = self.get_collection()
            if collection is None:
                return False, "Failed to get collection"
            
            # Test basic operation
            doc_count = collection.count_documents({})
            
            return True, f"Connection successful. Found {doc_count} documents in collection."
        
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def insert_document(self, document: dict, collection_name: str = "statements"):
        """Insert a document into the specified collection"""
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                raise Exception("Failed to connect to collection")
            
            # Add metadata
            document['uploaded_at'] = datetime.now().isoformat()
            document['processed_by'] = 'streamlit_app'
            
            # Insert document
            result = collection.insert_one(document)
            
            self.logger.info(f"Document inserted with ID: {result.inserted_id}")
            return result.inserted_id
        
        except Exception as e:
            self.logger.error(f"Failed to insert document: {str(e)}")
            raise
    
    def find_documents(self, query: dict = None, collection_name: str = "statements", sort_by: list = None):
        """Find documents in the specified collection"""
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                raise Exception("Failed to connect to collection")
            
            if query is None:
                query = {}
            
            cursor = collection.find(query)
            
            if sort_by:
                cursor = cursor.sort(sort_by)
            
            return list(cursor)
        
        except Exception as e:
            self.logger.error(f"Failed to find documents: {str(e)}")
            raise
    
    def count_documents(self, query: dict = None, collection_name: str = "statements"):
        """Count documents in the specified collection"""
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return 0
            
            if query is None:
                query = {}
            
            return collection.count_documents(query)
        
        except Exception as e:
            self.logger.error(f"Failed to count documents: {str(e)}")
            return 0
    
    def close_connection(self):
        """Close database connection"""
        try:
            if self._client:
                self._client.close()
                self._client = None
                self._db = None
                self._collection = None
                self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing connection: {str(e)}")

# Global database connection instance
db_connection = DatabaseConnection()