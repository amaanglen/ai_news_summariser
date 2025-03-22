# AI News Summariser

## Documentation

### Project Setup

#### Prerequisites
Ensure you have Python 3.7+ installed on your system. You also need the following dependencies:
```sh
pip install streamlit requests beautifulsoup4 gtts python-dotenv google-generativeai
```

### Environment Variables
Create a `.env` file in the project root and add the following keys:
```
GEMINIAPI_KEY=your_google_genai_api_key
NEWS_KEY=your_newsapi_key
```

### Running the Application
Start the Streamlit application using:
```sh
streamlit run app.py
```

## Model Details

### Summarization
The application uses **Google Gemini AI (gemini-2.0-flash)** to generate summaries of news articles. It extracts relevant information and provides structured insights. 

### Sentiment Analysis
The same Google Gemini AI model analyzes the sentiment of articles as **Positive, Negative, or Neutral**, providing a sentiment breakdown for each article and an overall sentiment summary. 

### Text-to-Speech (TTS)
The **Google Text-to-Speech (gTTS)** library converts the Hindi-translated summary into an audio file that users can play directly from the Streamlit interface.

## API Development

### Fetching News Articles
The application fetches news articles using **NewsAPI** ([newsapi.org](https://newsapi.org/v2/everything)) with search queries based on the company name.

- **Method:** `GET`
- **Parameters:**
  - `pageSize`: Number of articles to retrieve
  - `q`: Company name
  - `apiKey`: API key from environment variables
  - `sortBy`: Relevancy

### Web Scraping
To extract full article content, the application scrapes web pages using **BeautifulSoup**. It searches common HTML tags like `<article>`, `<main>`, and `<p>` to extract readable content.

### Google Gemini AI Integration
The **Google Generative AI API** processes the scraped content to:
1. Generate a structured summary.
2. Perform sentiment analysis.
3. Provide keyword extraction and comparative analysis.

### Hindi Translation & TTS
The English summary is translated to Hindi using the **Gemini AI API**. Then, the translated text is processed through **gTTS** for audio generation.

## API Usage

### Third-Party APIs Used
1. **NewsAPI**: Fetches news articles about a given company.
2. **Google Gemini AI**: Processes summarization, sentiment analysis, and translation.
3. **gTTS (Google Text-to-Speech)**: Converts Hindi-translated summaries into speech.

### Integration Details
- **NewsAPI**: Integrated via HTTP requests with API key authentication.
- **Google Gemini AI**: Requires API key authentication for AI-powered processing.
- **gTTS**: Operates locally and does not require an external API key.

## Assumptions & Limitations

### Assumptions
1. News articles retrieved from NewsAPI contain valid and relevant content.
2. Google Gemini AI provides accurate and meaningful analysis.
3. Users have a stable internet connection to interact with APIs.

### Limitations
1. **Google Gemini API Dependency**: If the API is unavailable, summarization and sentiment analysis will not work.
2. **NewsAPI Free Tier Limitations**: The free version has request limits and may not always return the latest articles.
3. **Web Scraping Restrictions**: Some websites may block automated scraping, leading to missing content.
4. **Hindi Translation Accuracy**: AI-generated translations may not always be perfectly natural or contextually accurate.
5. **TTS Quality**: The gTTS library may not support all Hindi phonetics and pronunciations perfectly.
