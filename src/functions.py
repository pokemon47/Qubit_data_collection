# attempt.py

import os
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import copy
import re
from time_interval import add_interval

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'


# Load environment variables
load_dotenv()
alpha_vantage_key = os.getenv("ALPHA_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
mongo_uri = os.getenv("MONGO_URI")


try:
    client: MongoClient = MongoClient(mongo_uri)  # 5 sec timeout
    db = client["quant_data"]

    # Check connection
    print(client.server_info())  # Should print server details

except Exception as e:
    print("MongoDB connection error:", e)

# Function to get news data from Alpha Vantage


def get_news_data_av(tickers=None, time_from=None, time_to=None, sort='LATEST', limit=10):
    base_url = 'https://www.alphavantage.co/query'

    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': tickers,
        'apikey': alpha_vantage_key,
        'sort': sort,
        'limit': limit
    }

    if time_from and time_to:
        params['time_from'] = time_from
        params['time_to'] = time_to
    else:
        params['time_from'] = (
            datetime.now() - timedelta(days=1)).strftime('%Y%m%dT%H%M')
        params['time_to'] = datetime.now().strftime('%Y%m%dT%H%M')

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Function to get top gainers and losers from Alpha Vantage


def get_top_gainers_losers_av():
    base_url = 'https://www.alphavantage.co/query'

    params = {
        'function': 'TOP_GAINERS_LOSERS',
        'apikey': alpha_vantage_key,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Function to get news data from News API


def get_news_data_n(name, from_date=None, to_date=None, sort_by="popularity", language="en"):
    base_url = "https://newsapi.org/v2/everything"
    keywords_cond = "(scandal OR lawsuit OR legal OR quarterly OR buyback OR merger OR losses OR performance OR disruption OR innovation OR investigation OR profits OR market OR regulatory OR trade OR economic OR layoffs OR funding OR regulation OR investment OR failed OR shareholder OR inflation OR earnings OR battle OR corporate OR ceo OR capital OR price OR outlook OR acquisition OR report OR scandal OR IPO OR fraud OR concerns OR profit OR failure OR debt OR announcement OR positive)"

    params = {
        'apiKey': news_api_key,
        'q': f"{name} AND {keywords_cond}",  # The search query (e.g., "apple")
        # Language for the articles (e.g., 'en' for English)
        'language': language,
        'sortBy': sort_by,  # Sort articles by 'relevancy', 'popularity', or 'publishedAt'
    }

    time_now = datetime.now()

    if from_date and to_date:
        params['from'] = from_date
        params['to'] = to_date
    else:
        # Default to 7 days ago if not provided
        params['from'] = (time_now - timedelta(days=7)).strftime('%Y-%m-%d')
        params['to'] = time_now.strftime('%Y-%m-%d')

    # Make the GET request
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        formatted_data = formattingADAGE(
            response.json(), time_now.strftime("%Y-%m-%d %H:%M:%S"), "news_api_org")
        # Do not want to be writing data to the database during testing
        if os.getenv("TEST_MODE", "false").lower() != "true":
            write_to_database(response.json(), "news_api_org")
            from_date_dmY = datetime.strptime(
                params['from'], "%Y-%m-%d").strftime("%d-%m-%Y")
            to_date_dmY = datetime.strptime(
                params['to'], "%Y-%m-%d").strftime("%d-%m-%Y")
            add_new_index(name, from_date_dmY, to_date_dmY)

        else:
            print("TESTING IN PROGRESS: TEST_MODE is True, not writing to database")
        return formatted_data
    else:
        return f"Error: {response.status_code}, {response.text}"


# Function which converts data from the APIs into the format which is stored
# in the database, and in the events[] list of the ADAGE 3.0 format


def create_article_list(data):
    article_list = []

    for articles in data.get("articles", []):
        # timestamp is in ISO 8601 format
        timestamp = articles.get("publishedAt", "unknown")
        if timestamp.endswith("Z"):
            timestamp = timestamp.replace("Z", "+00:00")
        article_data = {
            "time_object": {
                "timestamp": datetime.fromisoformat(timestamp),
                "duration": None,
                "duration_unit": None,
                "timezone": "UTC"
            },
            "event_type": "News article",
            "attribute": {
                "publisher": articles.get("source", {}).get("name", "unknown"),
                "title": articles.get("title", "unknown"),
                "author": articles.get("author", "unknown"),
                "description": articles.get("description", "unknown"),
                "url": articles.get("url", "none")
            }
        }

        article_list.append(article_data)

    return article_list

# Function which converts data from the APIs to ADAGE 3.0 format


def formattingADAGE(data, time_now, source_name):
    adage_data = {
        "data_source": str,
        "dataset_type": str,
        "dataset_id": str,
        "time_object": {
            "timestamp": datetime,
            "timezone": "UTC",
        },
        "events": []
    }
    if (source_name == "news_api_org"):
        adage_data["data_source"] = source_name
        adage_data["dataset_type"] = "News data"
        adage_data["dataset_id"] = "1"
        adage_data["time_object"]["timestamp"] = time_now

        article_list = copy.deepcopy(create_article_list(data))
        adage_data["events"] = article_list

    return adage_data

# Function which writes collected data to the database


def write_to_database(data, source_name):
    article_list = copy.deepcopy(create_article_list(data))

    # A separate collection is required for each source, since we must reconstruct
    # the ADAGE (including the data_source field) when retreiving data
    if (source_name == "news_api_org"):
        collection = db["news_api"]
    else:
        # news_articles is the default collection to insert into
        collection = db["news_articles"]

    insert_result = collection.insert_many(article_list)
    print(f"Inserted {len(insert_result.inserted_ids)} documents.")


def add_new_index(name, from_date, to_date):
    name_lower = name.strip().lower()

    interval_collection = db["company_index"]
    result = interval_collection.find_one(
        {"name": name_lower}, {"_id": 0, "intervals": 1})

    query = {}
    update = {}  # NEW
    if result:
        intervals = result.get("intervals", [])
        add_interval(intervals, from_date, to_date)

        # 3 LINES BELOW ARE OLD
        # query["item"] = "name"
        # query["$set"] = {"time_intervals": intervals}
        # interval_collection.update_one(query)

        # 3 LINES BELOW ARE NEW
        query["name"] = name_lower
        update["$set"] = {"time_intervals": intervals}
        interval_collection.update_one(query, update)

    else:
        query = {
            "name": name_lower,
            "time_intervals": [[from_date, to_date]],
            "hits": 0,
            "misses": 0
        }

        interval_collection.insert_one(query)


def company_to_ticker(name: str):
    base_url = "https://query2.finance.yahoo.com/v1/finance/search"

    params = {
        'q': name
    }

    response = requests.get(base_url, params=params, headers={
                            'User-Agent': user_agent})

    if response.status_code == 200:
        data = response.json()
        ticker = data['quotes'][0]['symbol']
        return {
            "ticker": ticker
        }
    else:
        return f"Error: {response.status_code}, {response.text}"


def ticker_to_company(ticker: str):
    base_url = "https://query2.finance.yahoo.com/v1/finance/search"

    params = {
        'q': ticker
    }

    response = requests.get(base_url, params=params, headers={
                            'User-Agent': user_agent})

    if response.status_code == 200:
        data = response.json()
        full_name = data['quotes'][0]['longname']

        name_split = re.split(r"\W+", full_name.lower())
        name = name_split[0]

        return {
            "short_name": name,
            "full_name": full_name
        }

    else:
        return f"Error: {response.status_code}, {response.text}"


# Make a job scheduler function,
# a job that is to be executed on a seperate thread once a day.
# The job is to make N number of consecutive requests with every K minutes.
# - not certainly required, could change based on learning more about AWS lambda
