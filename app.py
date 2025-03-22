import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import time
import base64
from gtts import gTTS
import io

from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

gemini_key = os.getenv("GEMINIAPI_KEY")
news_key = os.getenv("NEWS_KEY")



# Check for Google API dependency
try:
    from google import genai
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Set page configuration
st.set_page_config(
    page_title="Company News Analyzer",
    page_icon="🍉",
    layout="wide"
)

# Initialize session state variables
if 'hindi_summary' not in st.session_state:
    st.session_state.hindi_summary = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'company_analyzed' not in st.session_state:
    st.session_state.company_analyzed = None
if 'hindi_audio' not in st.session_state:
    st.session_state.hindi_audio = None

# Title and description
st.title("Company News Analyzer")
st.markdown("Get summaries and sentiment analysis of recent news about any company.")

# News API function
def get_company_news(company_name, api_key=news_key, num_articles=25):
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': company_name,
        'apiKey': api_key,
        'pageSize': num_articles,
        'sortBy': 'relevancy'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            news_data = response.json()
            
            if news_data.get('articles'):
                article_urls = []
                for article in news_data['articles']:
                    if article.get('url'):
                        article_urls.append({
                            'url': article['url'],
                            'title': article.get('title', 'No title'),
                            'source': article.get('source', {}).get('name', urlparse(article['url']).hostname)
                        })
                return article_urls
            else:
                return f"Error: No articles found for {company_name}"
        else:
            return f"Error: NewsAPI returned status code {response.status_code}"
    except Exception as e:
        return f"Error connecting to NewsAPI: {str(e)}"

# Web scraping function
def scrape_webpage(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Content unavailable (Status code: {response.status_code})"

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to get article content from common article containers
        article_content = ""
        
        # Look for article body in common containers
        article_tags = soup.find_all(['article', 'main', 'div'], class_=['article', 'content', 'post', 'entry'])
        if article_tags:
            for tag in article_tags:
                article_content += tag.get_text() + " "
        
        # If no article containers found, get paragraphs
        if not article_content:
            paragraphs = soup.find_all('p')
            article_content = ' '.join([p.get_text() for p in paragraphs])
        
        # If still no content, get body text
        if not article_content:
            article_content = soup.body.get_text() if soup.body else "No content found"
        
        # Clean up text
        cleaned_text = ' '.join(article_content.split())
        
        # Truncate very long articles
        if len(cleaned_text) > 8000:
            cleaned_text = cleaned_text[:8000] + "..."
        
        return cleaned_text
    except Exception as e:
        return f"Unable to scrape content: {str(e)}"

# Function to translate text to Hindi
def translate_to_hindi(text, company_name):
    if not GOOGLE_API_AVAILABLE:
        st.error("Google GenAI library not installed. Please install with: pip install google-generativeai")
        return None
    
    try:
        client = genai.Client(api_key=gemini_key)
        instructions = f"""
        Please translate the following English analysis about {company_name} into Hindi.
        Create a concise summary (about 100 words) that captures the main points and overall sentiment.
        The translation should be natural and fluent Hindi, suitable for audio conversion.
        Do not include any special characters, even new line.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=instructions + "\n\n" + text
        )
        
        return response.text
    except Exception as e:
        st.error(f"Error translating to Hindi: {str(e)}")
        return None

# Updated function to convert text to speech and get audio data
def get_audio_data(text):
    try:
        # For debugging (without using st.debug which doesn't exist)
        st.info(f"Processing Hindi text of length: {len(text)}")
        
        # Create audio with gTTS
        tts = gTTS(text=text, lang='hi', slow=False)
        
        # Save to BytesIO
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)  # Reset pointer to beginning of file
        
        # Return the audio bytes
        return fp.getvalue()
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

# Analysis generation function
def analyze_news(company_name, num_articles):
    if not GOOGLE_API_AVAILABLE:
        st.error("Google GenAI library not installed. Please install with: pip install google-generativeai")
        return None
    
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    # Step 1: Get news articles
    progress_text.text("Searching for news articles...")
    articles = get_company_news(company_name, num_articles=num_articles)
    
    if isinstance(articles, str):
        progress_text.text("")
        progress_bar.empty()
        st.error(articles)
        return None
    
    # Step 2: Scrape content
    progress_text.text(f"Found {len(articles)} articles. Scraping content...")
    article_contents = []
    
    for i, article in enumerate(articles):
        progress_bar.progress((i / len(articles)) * 0.5)  # First half of progress bar
        progress_text.text(f"Scraping {i+1}/{len(articles)}: {article['title']}")
        
        content = scrape_webpage(article['url'])
        article_contents.append({
            'title': article['title'],
            'source': article['source'],
            'content': content
        })
        time.sleep(0.5)  # Small delay to avoid rate limiting
    
    # Step 3: Prepare prompt
    progress_text.text("Preparing analysis prompt...")
    progress_bar.progress(0.6)
    
    prompt = "Please analyze the following news articles about " + company_name + ":\n\n"
    
    for article in article_contents:
        prompt += f"ARTICLE FROM: {article['source']}\n"
        prompt += f"TITLE: {article['title']}\n"
        prompt += f"CONTENT: {article['content']}\n\n"
    
    # Step 4: Generate analysis
    progress_text.text("Generating analysis with Gemini AI...")
    progress_bar.progress(0.7)
    
    try:
        client = genai.Client(api_key=gemini_key)
        instructions = f"""
        For these news articles about {company_name}, please provide:
        1. A brief summary of each article
        2. Sentiment analysis for each article (positive, negative, or neutral)
        3. Overall sentiment analysis across all articles
        4. Key themes or trends identified
        5. Comparative analysis of the articles
        6. Any notable contradictions or differences in reporting
        7. Mention the key words
        
        Format the response with clear headings and bullet points where appropriate.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=instructions + "\n\n" + prompt
        )
        
        progress_bar.progress(1.0)
        progress_text.text("Analysis complete!")
        time.sleep(1)
        progress_text.empty()
        progress_bar.empty()
        
        return response.text
    except Exception as e:
        progress_text.empty()
        progress_bar.empty()
        st.error(f"Error generating analysis: {str(e)}")
        return None

# Callback for Hindi button
def on_hindi_button_click():
    # This will trigger the translation and audio generation
    if st.session_state.analysis_result:
        with st.spinner("Generating Hindi summary..."):
            hindi_text = translate_to_hindi(st.session_state.analysis_result, st.session_state.company_analyzed)
            if hindi_text:
                st.session_state.hindi_summary = hindi_text
                # Pre-generate audio to ensure it's ready
                audio_data = get_audio_data(hindi_text)
                if audio_data:
                    st.session_state.hindi_audio = audio_data
                else:
                    st.session_state.hindi_audio = None
                    st.error("Failed to generate audio from Hindi text")
            else:
                st.error("Failed to generate Hindi translation")

# Main app interface
if not GOOGLE_API_AVAILABLE:
    st.warning("Google GenAI library not installed. Install with: pip install google-generativeai")

with st.form("news_analyzer_form"):
    company_name = st.text_input("Enter company name:", placeholder="e.g., Apple, Tesla, Microsoft")
    num_articles = st.slider("Number of articles to analyze:", min_value=10, max_value=25, value=15)
    submitted = st.form_submit_button("Analyze News")

# Show examples
with st.expander("Example companies to try"):
    st.markdown("""
    - Tech: Apple, Microsoft, Google, Meta, NVIDIA
    - Auto: Tesla, Ford, Toyota, General Motors
    - Finance: JPMorgan Chase, Bank of America, Goldman Sachs
    - Retail: Amazon, Walmart, Target
    - Energy: ExxonMobil, Chevron, Shell
    """)

# Process form submission
if submitted and company_name:
    # Reset the Hindi summary and audio when analyzing a new company
    st.session_state.hindi_summary = None
    st.session_state.hindi_audio = None
    st.session_state.company_analyzed = company_name
    
    st.subheader(f"News Analysis for {company_name}")
    
    with st.spinner("Analyzing news..."):
        result = analyze_news(company_name, num_articles)
    
    if result:
        # Store result in session state
        st.session_state.analysis_result = result
        
        # Display the result
        st.markdown("## Analysis Results")
        st.markdown(result)
        
        # Add download button
        st.download_button(
            label="Download Analysis",
            data=json.dumps({
                "company": company_name,
                "analysis": result,
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
            }, indent=2),
            file_name=f"{company_name.lower().replace(' ', '_')}_analysis.json",
            mime="application/json"
        )

# Display Hindi summary section if we have analysis results
if st.session_state.analysis_result:
    st.markdown("## Hindi Summary")
    
    # Hindi button that uses a callback
    if st.button("Generate & Play Hindi Summary", on_click=on_hindi_button_click):
        pass  # The actual work happens in the callback
    
    # Display Hindi text and audio if available
    if st.session_state.hindi_summary:
        st.markdown("### Hindi Text")
        st.markdown(st.session_state.hindi_summary)
        
        # Display audio if available in session state
        if st.session_state.hindi_audio:
            st.markdown("### Audio")
            # Try with explicit base64 encoding
            try:
                audio_bytes = st.session_state.hindi_audio
                # Use st.audio with correct format
                st.audio(audio_bytes, format="audio/mp3")
            except Exception as e:
                st.error(f"Error playing audio: {str(e)}")
                # Try alternative approach with base64
                try:
                    audio_str = base64.b64encode(audio_bytes).decode()
                    st.markdown(f'<audio controls><source src="data:audio/mp3;base64,{audio_str}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                except Exception as e2:
                    st.error(f"Alternative audio method also failed: {str(e2)}")
        else:
            # If audio wasn't pre-generated in the callback, try again
            with st.spinner("Processing audio..."):
                # Add a small delay to ensure text is fully processed
                time.sleep(1)
                audio_data = get_audio_data(st.session_state.hindi_summary)
                
            if audio_data:
                st.session_state.hindi_audio = audio_data
                st.markdown("### Audio")
                st.audio(audio_data, format="audio/mp3")
            else:
                st.error("Failed to generate audio. Please try again.")

# Footer
st.markdown("---")
st.markdown("Powered by NewsAPI, Gemini AI, and Streamlit")