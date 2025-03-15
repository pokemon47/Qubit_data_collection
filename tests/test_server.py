import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
from src.server import news_alpha_vantage,top_gainers_losers, newsapi

class testServer(unittest.TestCase):
    
    # @patch('requests.get')
    # def test_get_news_data_av_failure(self, mock_get):
    # """Test failure response from Alpha Vantage News API"""
    # mock_response = MagicMock()
    # mock_response.status_code = 400
    # mock_response.text = "Bad Request"
    # mock_get.return_value = mock_response

    # response = get_news_data_av()
    # self.assertTrue("Error: 400" in response)
    
    @patch('requests.get')
    def test_get_alpha_vantage(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 400
        
    
    print("here")

if __name__ == "__main__":
    unittest.main()