import unittest
from datetime import datetime, timedelta
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from attempt import get_news_data_av, get_top_gainers_losers_av, get_news_data_n, formattingADAGE

class testApiFetchCalls(unittest.TestCase):

    def test_get_news_data_av_real(self):
        result = get_news_data_av(tickers="AAPL")
        ## making sure we get a result:
        self.assertIsInstance(result, dict)
        self.assertIn("feed", result)

    def test_get_top_gainers_losers_av_real(self):
        result = get_top_gainers_losers_av()
        self.assertIsInstance(result, dict)
        self.assertIn("metadata", result)

    def test_get_news_data_n_real(self):
        result = get_news_data_n("facebook")
        self.assertIsInstance(result, dict)
        self.assertIn("events", result)

    def test_formattingADAGE(self):
        sample_data = {
                "status": "ok",
                "totalResults": 6040,
                "articles": [ {
                "source": {
                    "id": "null",
                    "name": "Gizmodo.com"
                },
                "author": "Matthew Gault",
                "title": "Musk and Trump’s Fort Knox Trip Is About Bitcoin",
                "description": "More than a stunt, the Fort Knox visit might be a chance for the President to change the price of gold and dump the price hike into cryptocurrency.",
                "url": "https://gizmodo.com/musk-and-trumps-fort-knox-trip-is-about-bitcoin-2000569420",
                "urlToImage": "https://gizmodo.com/app/uploads/2024/10/sec-bitcoin-hack-arrest.jpg",
                "publishedAt": "2025-02-27T19:05:24Z",
                "content": "Can a President make money out of thin air? On paper, yes.\r\nDonald Trump and Elon Musk have been talking a lot about Fort Knox lately, the place where America keeps its official gold reserves. Both h… [+3792 chars]"
                },
                {
                "source": {
                    "id": "the-verge",
                    "name": "The Verge"
                },
                "author": "Vox Creative",
                "title": "Five predictions for where crypto is headed in 2025",
                "description": "Crypto is, once again, exploding. Momentum born of a potentially friendlier regulatory atmosphere has met rising coin values, with Bitcoin more than doubling in value last year. Meanwhile, powered by advances to the underlying infrastructure, crypto is evolvi…",
                "url": "https://www.theverge.com/ad/612525/five-predictions-for-crypto-2025-saga",
                "urlToImage": "https://platform.theverge.com/wp-content/uploads/sites/2/2025/02/VG24_Saga_1660442_Lede_V1.png?quality=90&strip=all&crop=0%2C29.057591623037%2C100%2C41.884816753927&w=1200",
                "publishedAt": "2025-02-26T18:34:53Z",
                "content": "Crypto is, once again, exploding. Momentum born of a potentially friendlier regulatory atmosphere has met rising coin values, with Bitcoin more than doubling in value last year. Meanwhile, powered by… [+6145 chars]"
                }]
            }

        formatted_result = formattingADAGE(sample_data, "2025-03-15 12:30:00", "news_api_org")
        self.assertEqual(formatted_result["data_source"], "news_api_org")
        self.assertEqual(formatted_result["dataset_type"], "News data")
        self.assertEqual(len(formatted_result["events"]), 2)
        self.assertEqual(formatted_result["events"][0]["attribute"]["title"], "Musk and Trump’s Fort Knox Trip Is About Bitcoin")
        self.assertEqual(formatted_result["events"][1]["attribute"]["title"], "Five predictions for where crypto is headed in 2025")


if __name__ == "__main__":
    unittest.main()
