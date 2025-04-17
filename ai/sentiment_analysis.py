from newsapi import NewsApiClient
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

def get_sentiment():
    headlines = fetch_headlines("nifty OR bank nifty OR sensex")

    if not headlines:
        return "neutral"

    prompt = f"Classify the market sentiment of these headlines as positive, neutral, or negative:\n\n" + "\n".join(headlines)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0.2
    )

    sentiment = response.choices[0].message['content'].lower().strip()
    return sentiment

def fetch_headlines(query):
    articles = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=5)
    return [a['title'] for a in articles['articles']]
