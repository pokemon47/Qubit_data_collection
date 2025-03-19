import os
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import copy

# Load environment variables
load_dotenv()
alpha_vantage_key = os.getenv("ALPHAVANTAGE_K EY")
news_api_key = os.getenv("NEWSAPI_KEY")
# news_api_key = '4141137ea3eb462485cfd4b63e904bad'
# alpha_vantage_key = 'XXO345Z81O5RS7YR'

# Load MongoDB connection URI
# Load .env variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

try:
    client = MongoClient(mongo_uri)  # 5 sec timeout
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
        params['time_from'] = (datetime.now() - timedelta(days=1)).strftime('%Y%m%dT%H%M')
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
    keywords_cond= "(scandal OR lawsuit OR legal OR quarterly OR buyback OR merger OR losses OR performance OR disruption OR innovation OR investigation OR profits OR market OR regulatory OR trade OR economic OR layoffs OR funding OR regulation OR investment OR failed OR shareholder OR inflation OR earnings OR battle OR corporate OR ceo OR capital OR price OR outlook OR acquisition OR report OR scandal OR IPO OR fraud OR concerns OR profit OR failure OR debt OR announcement OR positive)"

    params = {
        'apiKey': news_api_key,
        'q': f"{name} AND {keywords_cond}",  # The search query (e.g., "apple")
        'language': language,  # Language for the articles (e.g., 'en' for English)
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
        formatted_data = formattingADAGE(response.json(), time_now.strftime("%Y-%m-%d %H:%M:%S"), "news_api_org")
        return formatted_data
    else:
        return f"Error: {response.status_code}, {response.text}"

# Function to map company names to tickers
def tickers_fetch(name):
    url = f'https://stock-symbol-lookup-api.onrender.com/{name}'
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Function which converts data from the APIs into the format which is stored
# in the database, and in the events[] list of the ADAGE 3.0 format    
def create_article_list(data):
    article_list = []

    for articles in data.get("articles", []):
        article_data = {
            "time_object": {
                "timestamp": datetime.fromisoformat(articles.get("publishedAt", "unknown")),
                "duration": None,
                "duration_unit": None,
                "timezone": "UTC"
            },
            "event_type": "News article",
            "attribute": {
                "publisher": articles.get("source", {}).get("name", "unknown"),
                "title": articles.get("title", "unknown"),
                # "tickers": (to be implemented later)
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


# Make a job scheduler fucntion,
# a job that is to be executed on a seperate thread once a day.
# The job is to make N number of consecutive requests with every K minutes.
# - not certainly required, could change based on learning more about AWS lambda
