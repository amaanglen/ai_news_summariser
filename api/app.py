from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from google import genai

app = Flask(__name__)



def get_company_news(company_name, api_key='8d71b452dc7640b0b67a3e4d2183a683', num_articles=25):
    # Define the base URL and parameters for the NewsAPI request
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': company_name,  # Search query (company name)
        'apiKey': api_key,   # API key
        'pageSize': num_articles,  # Number of articles to return
        'sortBy': 'relevancy'  # Sort by relevancy
    }

    # Make the GET request to the NewsAPI
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        news_data = response.json()

        # Extract the URLs of the articles
        article_urls = []
        for article in news_data['articles']:
            article_urls.append(article['url'])

        return article_urls
    else:
        return f"Error: Unable to fetch news (status code: {response.status_code})"

def scrape_webpage(url):


    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        return "IGNORE THIS ARTICLE"
        # raise Exception(f"Error: Unable to access the webpage (Status code: {response.status_code})")

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the text content from the webpage
    text = soup.get_text()

    # Clean up the text by removing excessive whitespace and newlines
    cleaned_text = ' '.join(text.split())

    # Return the cleaned text
    return cleaned_text


def create_prompt(company_name):
    urls = get_company_news(company_name)
    prompt = ''
    for i in range(len(urls)):
        prompt += f"\n\n THIS ARTICLE IS FROM {urlparse(urls[i]).hostname} \n\n"
        prompt += scrape_webpage(urls[i])

    return prompt


def gpt_output(company_name):

    client = genai.Client(api_key="AIzaSyCInk9NK8rrBBmxm3Uk_QHjFygk7fXZrmg")
    prompt = create_prompt(company_name)
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

