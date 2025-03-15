import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# alpha_vantage_key = os.getenv("ALPHAVANTAGE_K EY")
alpha_vantage_key = 'XXO345Z81O5RS7YR'
# news_api_key = os.getenv("NEWSAPI_KEY")
news_api_key = '4141137ea3eb462485cfd4b63e904bad'

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
        
        for articles in data.get("articles", []):
            event_data = {
                "time_object": {
                    "timestamp": articles.get("publishedAt", "unknown"),
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
            adage_data["events"].append(event_data)
    return adage_data

# Make a job scheduler fucntion,
# a job that is to be executed on a seperate thread once a day.
# The job is to make N number of consecutive requests with every K minutes.
# - not certainly required, could change based on learning more about AWS lambda
