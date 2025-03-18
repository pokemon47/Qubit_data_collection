from server import app
import unittest
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))
from server import app


class testQubitApis(unittest.TestCase):

    # classmethod -> runs before the tests start
    # starts the app basically:
    @classmethod
    def set_up_class(cls):
        cls.app = app.test_client()

    # before tests
    # basically beforeEach
    def set_up(self):
        self.client = self.app

    def test_set_up(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(
            "utf-8"), "Hello, Flask is working!")

    # def test_news_alpha_vantage_valid(self):
    #     response = self.app.get("/news_alpha_vantage?tickers=AAPL&limit=5")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("feed", response.get_json())

    # def test_news_alpha_vantage_invalid(self):
    #     response = self.app.get("/news_alpha_vantage")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(response.get_json(), dict)

    # def test_top_gainers_losers(self):
    #     response = self.app.get("/top_gainers_losers")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(response.get_json(), dict)

    def test_newsapi(self):
        # testing the correct flow - i.e. every parameter is correct
        response = self.app.get("/newsapi?name=Facebook")
        self.assertEqual(response.status_code, 200)
        self.assertIn("events", response.get_json())

    def test_newsapi_missing_name(self):
        # no name paramater given --> return error code 400 + errr msg
        response = self.app.get(
            "/newsapi?from_date=2025-03-04&to_date=2025-03-10")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Invalid 'name' given"})

    def test_newsapi_invalid_name(self):
        # name has AND operation --> invalid name --> return code 400 + err msg
        response = self.app.get(
            "/newsapi?name=Facebook+AND+Apple&from_date=2025-03-04&to_date=2025-03-10")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Invalid 'name' given"})

    def test_newsapi_missing_dates(self):
        # only one date provided -> 400 + err msg
        response = self.app.get("/newsapi?name=Apple&from_date=2025-03-04")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Please provide both to and from dates or none"})

    def test_newsapi_invalid_date_format(self):
        # incorrect date format -> 400 + err msg
        response = self.app.get(
            "/newsapi?name=Facebook&from_date=03-04-2025&to_date=2025/03/10")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Date values must be of ISO 8601 format (e.g. 2025-03-04 or 2025-03-04T07:11:59)"})


if __name__ == "__main__":
    unittest.main()
