# test_integration.py

import pytest
import json
import os
from unittest.mock import MagicMock, patch
from datetime import datetime
import mongomock
import requests
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv

# Import the app and functions to test
import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))
from server import app
from functions import get_news_data_n, formattingADAGE, create_article_list, write_to_database

load_dotenv()
news_api_key = os.getenv("NEWS_API_KEY")
# Sample mock response from News API
MOCK_NEWS_API_RESPONSE = {
    "status": "ok",
    "totalResults": 2,
    "articles": [
        {
            "source": {
                "id": "techcrunch",
                "name": "TechCrunch"
            },
            "author": "John Doe",
            "title": "Apple reports record quarterly earnings",
            "description": "Apple Inc. reported record earnings for the fourth quarter.",
            "url": "https://example.com/article1",
            "urlToImage": "https://example.com/image1.jpg",
            "publishedAt": "2025-03-15T12:30:45Z",
            "content": "Apple Inc. reported record earnings for the fourth quarter..."
        },
        {
            "source": {
                "id": "businessinsider",
                "name": "Business Insider"
            },
            "author": "Jane Smith",
            "title": "Apple's market cap reaches new heights",
            "description": "Apple's market capitalization has reached a new milestone.",
            "url": "https://example.com/article2",
            "urlToImage": "https://example.com/image2.jpg",
            "publishedAt": "2025-03-14T09:15:30Z",
            "content": "Apple's market capitalization has reached a new milestone..."
        }
    ]
}


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_env_setup(monkeypatch):
    """Setup environment variables for testing"""
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("NEWS_API_KEY", "fake_news_api_key")
    monkeypatch.setenv("ALPHA_API_KEY", "fake_alpha_api_key")
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
class TestNewsApiIntegration:
    
    @patch('requests.get')
    def test_get_news_data_n_external_api_call(self, mock_get, mock_mongo):
        """Test the external API call in get_news_data_n"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_NEWS_API_RESPONSE
        mock_get.return_value = mock_response
        
        # Call function
        result = get_news_data_n(name="Apple")
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        
        # Check base URL
        assert args[0] == "https://newsapi.org/v2/everything"
        
        # Check parameters include company name and API key
        assert "Apple" in kwargs['params']['q']
        assert kwargs['params']['apiKey'] == news_api_key
        
        # Check result has expected format
        assert "data_source" in result
        assert result["data_source"] == "news_api_org"
        assert "events" in result
        assert len(result["events"]) == 2
        
    def test_create_article_list_formatting(self):
        """Test the formatting of news articles"""
        article_list = create_article_list(MOCK_NEWS_API_RESPONSE)
        
        # Check we got the expected number of articles
        assert len(article_list) == 2
        
        # Check the structure of the first article
        article = article_list[0]
        assert "time_object" in article
        assert "event_type" in article
        assert "attribute" in article
        
        # Check specific fields
        assert article["event_type"] == "News article"
        assert article["attribute"]["title"] == "Apple reports record quarterly earnings"
        assert article["attribute"]["publisher"] == "TechCrunch"
        
        # Check datetime conversion
        assert isinstance(article["time_object"]["timestamp"], datetime)
        assert article["time_object"]["timezone"] == "UTC"
    
    @patch('requests.get')
    def test_full_api_integration(self, mock_get, mock_mongo, client):
        """Test the full API integration from route to database"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_NEWS_API_RESPONSE
        mock_get.return_value = mock_response
        
        # Make API request
        response = client.get('/newsapi?name=Apple&from_date=2025-03-10&to_date=2025-03-17')
        
        # Check response status
        assert response.status_code == 200
        
        # Check database was updated (this should be skipped in TEST_MODE)
        news_collection = mock_mongo["news_api"]
        company_index = mock_mongo["company_index"]
        
        # In TEST_MODE, no data should be written to database
        assert news_collection.count_documents({}) == 0
        assert company_index.count_documents({}) == 0
    
    @patch('requests.get')
    def test_write_to_database(self, mock_get, mock_mongo):
        """Test the database writing functionality"""
        # Turn off TEST_MODE for this test
        os.environ["TEST_MODE"] = "false"
        
        # Call the write_to_database function directly
        write_to_database(MOCK_NEWS_API_RESPONSE, "news_api_org")
        
        # Check database was updated
        news_collection = mock_mongo["news_api"]
        articles = list(news_collection.find({}))
        
        # Check that documents were inserted
        assert len(articles) == 2
        
        # Check structure of inserted documents
        article = articles[0]
        assert "time_object" in article
        assert "event_type" in article
        assert "attribute" in article
        
        # Restore TEST_MODE
        os.environ["TEST_MODE"] = "true"
    
    @patch('requests.get')
    def test_error_handling(self, mock_get, client):
        """Test error handling when the external API fails"""
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden: Invalid API key"
        mock_get.return_value = mock_response
        
        # Make API request
        response = client.get('/newsapi?name=Apple')
        
        # Parse response
        data = json.loads(response.data)
        
        # Check the error is properly returned
        assert "Error: 403" in data
    
    def test_adage_formatting(self):
        """Test the ADAGE formatting function"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_data = formattingADAGE(MOCK_NEWS_API_RESPONSE, current_time, "news_api_org")
        
        # Check structure
        assert formatted_data["data_source"] == "news_api_org"
        assert formatted_data["dataset_type"] == "News data"
        assert formatted_data["dataset_id"] == "1"
        assert formatted_data["time_object"]["timestamp"] == current_time
        assert len(formatted_data["events"]) == 2
    
    def test_input_validation(self, client):
        """Test input validation for the API endpoint"""
        # Test invalid company name with SQL injection attempt
        response = client.get('/newsapi?name=Apple OR 1=1')
        assert response.status_code == 400
        
        # Test missing date parameter
        response = client.get('/newsapi?name=Apple&from_date=2025-03-10')
        assert response.status_code == 400
        
        # Test invalid date format
        response = client.get('/newsapi?name=Apple&from_date=10-03-2025&to_date=17-03-2025')  
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main(["-xvs", "test_integration.py"])