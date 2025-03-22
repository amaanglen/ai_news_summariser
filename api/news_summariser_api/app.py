from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import asyncio
from google import genai

load_dotenv()  # Load .env file

gemini_key = os.getenv("GEMINIAPI_KEY")
news_key = os.getenv("NEWS_KEY")


app = Flask(__name__)

# Asynchronous function to get company news
async def get_company_news_async(company_name, api_key=news_key, num_articles=25):
    # Define the base URL and parameters for the NewsAPI request
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': company_name,  # Search query (company name)
        'apiKey': api_key,   # API key
        'pageSize': num_articles,  # Number of articles to return
        'sortBy': 'relevancy'  # Sort by relevancy
    }

    # Make the GET request to the NewsAPI
    response = await asyncio.to_thread(requests.get, url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        news_data = response.json()

        # Extract the URLs of the articles
        article_urls = [article['url'] for article in news_data['articles']]

        return article_urls
    else:
        raise Exception(f"Error: Unable to fetch news (status code: {response.status_code})")

# Asynchronous function to scrape a webpage
async def scrape_webpage_async(url):
    # Send a GET request to the URL
    response = await asyncio.to_thread(requests.get, url)

    # Check if the request was successful
    if response.status_code != 200:
        return "IGNORE THIS ARTICLE"

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the text content from the webpage
    text = soup.get_text()

    # Clean up the text by removing excessive whitespace and newlines
    cleaned_text = ' '.join(text.split())

    # Return the cleaned text
    return cleaned_text


# Creating the prompt for GPT-3 using async methods
async def create_prompt_async(company_name):
    urls = await get_company_news_async(company_name)
    prompt = ''
    for url in urls:
        prompt += f"\n\n THIS ARTICLE IS FROM {urlparse(url).hostname} \n\n"
        prompt += await scrape_webpage_async(url)
    return prompt





from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import asyncio
from google import genai
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()
app = Flask(__name__)

# Asynchronous function to get company news
async def get_company_news_async(company_name, api_key=news_key, num_articles=25):
    # Define the base URL and parameters for the NewsAPI request
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': company_name,  # Search query (company name)
        'apiKey': api_key,   # API key
        'pageSize': num_articles,  # Number of articles to return
        'sortBy': 'relevancy'  # Sort by relevancy
    }

    # Make the GET request to the NewsAPI
    response = await asyncio.to_thread(requests.get, url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        news_data = response.json()

        # Extract the URLs of the articles
        article_urls = [article['url'] for article in news_data['articles']]

        return article_urls
    else:
        raise Exception(f"Error: Unable to fetch news (status code: {response.status_code})")

# Asynchronous function to scrape a webpage
async def scrape_webpage_async(url):
    # Send a GET request to the URL
    response = await asyncio.to_thread(requests.get, url)

    # Check if the request was successful
    if response.status_code != 200:
        return "IGNORE THIS ARTICLE"

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the text content from the webpage
    text = soup.get_text()

    # Clean up the text by removing excessive whitespace and newlines
    cleaned_text = ' '.join(text.split())

    # Return the cleaned text
    return cleaned_text

# Creating the prompt for GPT-3 using async methods
async def create_prompt_async(company_name):
    urls = await get_company_news_async(company_name)
    prompt = ''
    for url in urls:
        prompt += f"\n\n THIS ARTICLE IS FROM {urlparse(url).hostname} \n\n"
        prompt += await scrape_webpage_async(url)
    return prompt

# Modified function to run async code properly
def gpt_output(company_name):
    client = genai.Client(api_key=gemini_key)
    
    # Get or create an event loop for the current thread
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run the async function using the event loop
    prompt = loop.run_until_complete(create_prompt_async(company_name))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""For the given set of articles from different sources, return the summary for each article, sentiment analysis and the comparative analysis.
        Refer to the articles as their source's name and the title. The articles: \n\n{prompt}""",
    )

    return response.text

@app.route('/get_company_summary', methods=['GET'])
def get_company_summary():
    # Get the company_name from the request arguments
    company_name = request.args.get('company_name')

    if not company_name:
        return jsonify({"error": "company_name is required"}), 400

    try:
        # Get the response from gpt_output
        result = gpt_output(company_name)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
