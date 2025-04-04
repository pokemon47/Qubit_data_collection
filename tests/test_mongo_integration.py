# test_mongodb_integration.py

import pytest
import os
from unittest.mock import patch, MagicMock
import mongomock
from datetime import datetime
from pymongo import MongoClient

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))

from functions import write_to_database, add_new_index, get_news_data_n
from time_interval import add_interval

# Sample mock response from News API (simplified)
MOCK_NEWS_API_RESPONSE = {
    "status": "ok",
    "totalResults": 1,
    "articles": [
        {
            "source": {"id": "test", "name": "Test Source"},
            "author": "Test Author",
            "title": "Test Title",
            "description": "Test Description",
            "url": "https://example.com/test",
            "publishedAt": "2025-03-15T12:30:45Z",
            "content": "Test content"
        }
    ]
}


@pytest.fixture
def mock_env_setup(monkeypatch):
    """Setup environment variables for testing"""
    monkeypatch.setenv("TEST_MODE", "false")  # Ensure DB writes are allowed
    monkeypatch.setenv("NEWS_API_KEY", "fake_news_api_key")
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017/")


@pytest.fixture
def mock_mongo(monkeypatch):
    """Create a mock MongoDB client using mongomock"""
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["quant_data"]
    
    # Create collections
    mock_db.create_collection("news_api")
    mock_db.create_collection("company_index")
    
    # Patch the MongoDB client
    monkeypatch.setattr("functions.client", mock_client)
    monkeypatch.setattr("functions.db", mock_db)
    
    return mock_db


@pytest.mark.usefixtures("mock_env_setup")
class TestMongoDBIntegration:
    
    def test_write_to_database(self, mock_mongo):
        """Test that article data is correctly written to MongoDB"""
        # Call the function that writes to the database
        write_to_database(MOCK_NEWS_API_RESPONSE, "news_api_org")
        
        # Verify data was written to the correct collection
        collection = mock_mongo["news_api"]
        articles = list(collection.find({}))
        
        assert len(articles) == 1
        article = articles[0]
        
        # Verify structure and content
        assert article["event_type"] == "News article"
        assert article["attribute"]["title"] == "Test Title"
        assert article["attribute"]["publisher"] == "Test Source"
        assert isinstance(article["time_object"]["timestamp"], datetime)
    
    def test_add_new_index_new_company(self, mock_mongo):
        """Test adding a new company index"""
        company_name = "TestCompany"
        from_date = "15-03-2025"
        to_date = "20-03-2025"
        
        # Call the function to add a new index
        add_new_index(company_name, from_date, to_date)
        
        # Verify data was written correctly
        collection = mock_mongo["company_index"]
        company_data = collection.find_one({"name": company_name})
        
        assert company_data is not None
        assert company_data["time_intervals"] == [[from_date, to_date]]
        assert company_data["hits"] == 0
        assert company_data["misses"] == 0
        
    @patch('requests.get')
    def test_full_db_integration_flow(self, mock_get, mock_mongo):
        """Test the complete flow from API call to database storage"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_NEWS_API_RESPONSE
        mock_get.return_value = mock_response
        
        # Call the function
        company_name = "TestCompany"
        from_date = "2025-03-15"
        to_date = "2025-03-20"
        result = get_news_data_n(name=company_name, from_date=from_date, to_date=to_date)
        
        # Verify data was written to the news collection
        news_collection = mock_mongo["news_api"]
        articles = list(news_collection.find({}))
        assert len(articles) == 1
        
        # Verify company index was updated
        company_collection = mock_mongo["company_index"]
        company_data = company_collection.find_one({"name": company_name})
        assert company_data is not None
        
        # Verify the returned data has the correct format
        assert result["data_source"] == "news_api_org"
        assert len(result["events"]) == 1


if __name__ == "__main__":
    pytest.main(["-xvs", "test_mongodb_integration.py"])