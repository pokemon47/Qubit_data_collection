# from server import app
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
    def setUpClass(cls):
        cls.app = app.test_client()

    # before tests
    # basically beforeEach
    def setUp(self):
        self.client = self.app
        os.environ["TEST_MODE"] = "True"

    def tearDown(self):
        os.environ.pop("TEST_MODE", None)
        
    def test_set_up(self):
        response = self.app.get("/status")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json.get("status"), "Server is running")

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

    def test_newsapi_with_dates(self):
        # testing the correct flow with start and end dates
        response = self.app.get("/newsapi?name=Facebook&from_date=2025-04-04&to_date=2025-04-10")
        self.assertEqual(response.status_code, 200)
        self.assertIn("events", response.get_json())

    def test_newsapi_missing_name(self):
        # no name paramater given --> return error code 400 + errr msg
        response = self.app.get(
            "/newsapi?from_date=2025-04-04&to_date=2025-04-10")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Invalid 'name' given"})

    def test_newsapi_invalid_name(self):
        # name has AND operation --> invalid name --> return code 400 + err msg
        response = self.app.get(
            "/newsapi?name=Facebook+AND+Apple&from_date=2025-04-04&to_date=2025-04-10")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Invalid 'name' given"})

    def test_newsapi_missing_dates(self):
        # only one date provided -> 400 + err msg
        response = self.app.get("/newsapi?name=Apple&from_date=2025-04-04")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Please provide both to and from dates or none"})

    def test_newsapi_invalid_date_format(self):
        # incorrect date format -> 400 + err msg
        response = self.app.get(
            "/newsapi?name=Facebook&from_date=04-04-2025&to_date=2025/04/10")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Date values must be of ISO 8601 format (e.g. 2025-03-04 or 2025-03-04T07:11:59)"})
        
    def test_company_to_ticker(self):
        # testing the correct flow
        test_cases = [
            ["apple", "AAPL"],
            ["google", "GOOG"],
            ["microsoft", "MSFT"],
            ["facebook", "META"],
            ["adobe", "ADBE"],
            ["amazon", "AMZN"],
            ["tesla", "TSLA"],
            ["atlassian", "TEAM"]
        ]

        for case in test_cases:
            response = self.app.get(f"/convert/company_to_ticker?name={case[0]}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), {
                            "ticker": case[1]})

    def test_company_to_ticker_no_name(self):
        # no name provided -> 400 + error msg
        response = self.app.get("/convert/company_to_ticker")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Invalid 'name' given"})

    def test_ticker_to_company(self):
        # testing the correct flow
        test_cases = [
            ["AAPL", "apple", "Apple Inc."],
            ["MSFT", "microsoft", "Microsoft Corporation"],
            ["ADBE", "adobe", "Adobe Inc."],
            ["AMZN", "amazon", "Amazon.com, Inc."],
            ["TSLA", "tesla", "Tesla, Inc."],
            ["TEAM", "atlassian", "Atlassian Corporation"]
        ]

        for case in test_cases:
            response = self.app.get(f"/convert/ticker_to_company?ticker={case[0]}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), {
                            "short_name": case[1],
                            "full_name": case[2]})

    def test_ticker_to_company_no_ticker(self):
        # no ticker provided -> 400 + error msg
        response = self.app.get("/convert/ticker_to_company")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
                         "error": "Invalid 'ticker' given"})


if __name__ == "__main__":
    unittest.main()
