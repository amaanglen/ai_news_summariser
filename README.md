# AI News Summarizer

## Documentation

### Project Setup

#### Prerequisites:
Ensure you have Python 3.8+ installed.

#### Installation Steps:

1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd ai_news_summariser
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add the API keys:
   ```sh
   GEMINIAPI_KEY=<your_google_gemini_api_key>
   NEWS_KEY=<your_newsapi_key>
   ```

5. Run the application:
   ```sh
   streamlit run app.py
   ```

---

## Model Details

The application utilizes the following models:

- **Summarization Model:** Google Gemini AI generates summaries of the scraped news articles.
- **Sentiment Analysis Model:** Google Gemini AI analyzes the sentiment of news articles, categorizing them as positive, negative, or neutral.
- **Text-to-Speech (TTS) Model:** Google Text-to-Speech (gTTS) converts Hindi summaries into audio output.

---

## Web Scraping Process

The application scrapes news articles using the following approach:

1. **Fetching HTML Content:** The `scrape_webpage` function sends an HTTP request to the news article URL and retrieves the HTML content.
2. **Parsing the Content:** BeautifulSoup is used to parse the HTML and extract the main article text, removing unnecessary elements like ads and navigation menus.
3. **Cleaning the Text:** The extracted text is cleaned by removing excessive whitespace, special characters, and non-relevant sections.
4. **Passing to AI Model:** The cleaned article text is then sent to Google Gemini AI for summarization and sentiment analysis.

---

## API Development

- **News Retrieval API:** The `get_company_news` function queries the NewsAPI to fetch the latest news articles related to a given company.
- **Web Scraping API:** The `scrape_webpage` function extracts the main text content from news articles using BeautifulSoup.
- **Analysis API:** The `analyze_news` function sends the extracted news content to Google Gemini AI for summarization and sentiment analysis.
- **Translation API:** The `translate_to_hindi` function translates the analysis results into Hindi.
- **Text-to-Speech API:** The `get_audio_data` function converts the Hindi summary into an audio file using gTTS.

---

## Deployment

The API is deployed using a Docker container on Hugging Face Spaces.

---

## Accessing APIs via Postman

- **News Retrieval API:**
  ```http
  GET https://newsapi.org/v2/everything?q=Apple&apiKey=<NEWS_KEY>
  ```

- **Web Scraping API:**
  ```http
  GET http://localhost:8501/scrape?url=<news_article_url>
  ```

- **Analysis API (Handled within the application workflow):**
  ```http
  POST http://localhost:8501/analyze
  ```

- **Translation API:**
  ```http
  POST http://localhost:8501/translate
  ```

- **Text-to-Speech API:**
  ```http
  GET http://localhost:8501/text-to-speech
  ```

---

## API Usage

- **NewsAPI:** Used to fetch the latest company news articles.
- **Google Gemini AI:** Used for summarization and sentiment analysis.
- **gTTS (Google Text-to-Speech):** Used for generating Hindi audio summaries.

---

## Assumptions & Limitations

### Assumptions:
- The Google Gemini AI key is valid and has sufficient quota.
- NewsAPI provides reliable and up-to-date articles.
- Web scraping is permitted by the respective news websites.

### Limitations:
- The free tier of NewsAPI has request limits.
- Google Gemini AI requires API key-based authentication.
- The summarization and sentiment analysis depend on the accuracy of the AI model.
- gTTS may not handle long summaries efficiently.
- Web scraping may fail if the article structure varies significantly.
