import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import requests
from datetime import datetime, timedelta
import sqlite3
from config.config import DB_PATH

class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')
        self.nlp = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
        self.news_api_key = "your_newsapi_key"  # Replace with actual key
        
    def get_news_sentiment(self, symbol, days=7):
        # Fetch news from NewsAPI
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        url = f"https://newsapi.org/v2/everything?q={symbol}&from={from_date}&sortBy=publishedAt&apiKey={self.news_api_key}"
        
        try:
            response = requests.get(url)
            articles = response.json().get('articles', [])
            
            sentiments = []
            for article in articles:
                text = f"{article['title']}. {article['description']}"
                result = self.nlp(text[:512])  # Truncate to BERT max length
                sentiments.append({
                    'date': article['publishedAt'],
                    'title': article['title'],
                    'sentiment': result[0]['label'],
                    'score': result[0]['score']
                })
            
            df = pd.DataFrame(sentiments)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Save to database
            self._save_to_db(symbol, df)
            
            return df
        except Exception as e:
            print(f"Error fetching news: {e}")
            return pd.DataFrame()
    
    def _save_to_db(self, symbol, df):
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(f"{symbol}_sentiment", conn, if_exists='replace', index=True)
        conn.close()
    
    def get_historical_sentiment(self, symbol):
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT * FROM {symbol}_sentiment"
        df = pd.read_sql(query, conn, parse_dates=['date'])
        conn.close()
        return df
