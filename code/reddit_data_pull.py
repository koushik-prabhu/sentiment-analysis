import praw
import pandas as pd
import re
import openpyxl
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class Reddit:
       def __init__(self):
              # credentials
              self.client_id = 'YDQ6fXLGW2FA8_M6w0K7bA'
              self.secret_id = 'gOVpXH-57GMNs8dgtUYaXZCe_BzH4w'
              self.user_agent = 'data-pipeline-test by u/Conscious_Rice1901'
              # Download VADER sentiment analyzer
              nltk.download('vader_lexicon')

              # reddit connection instance
              self.reddit = praw.Reddit(
                     client_id = self.client_id,
                     client_secret = self.secret_id,
                     user_agent = self.user_agent
              )

       def data_extraction(self):
       
              subreddits = ['OnePlus', 'Samsung', 'Apple', 'Google']
              keywords = ['OnePlus 11', 'Samsung Galaxy S23', 'iPhone 14', 'Google Pixel 7']

              reviews = []
              for subreddit in subreddits:
                     for post in self.reddit.subreddit(subreddit).search(' OR '.join(keywords)):
                            try:
                                   reviews.append({
                                          "brand": subreddit,
                                          "comment": post.selftext,
                                          "score": post.score
                                   })
                            except Exception:
                                   print('exception occured!')
              self.dataframe = pd.DataFrame(reviews)
       
       def data_preprocessing(self, text):
              text = text.lower()
              text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
              text = re.sub(r'[^\w\s]', '', text)
              text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
              return text
       
       def sentiment_analysis(self, text):
              # Initialize the VADER sentiment analyzer
              sia = SentimentIntensityAnalyzer()
              sentiment_scores = sia.polarity_scores(text)
              return sentiment_scores['compound']  # 'compound' gives an overall sentiment score

       def main(self):
              # extract data from reddit using reddit api
              self.data_extraction()
              # perform pre processing 
              self.dataframe = self.dataframe[self.dataframe['comment'].str.strip().astype(bool)]
              self.dataframe['processed comment'] = self.dataframe['comment'].apply(self.data_preprocessing)
              # Apply sentiment analysis
              self.dataframe['sentiment'] = self.dataframe['processed comment'].apply(self.sentiment_analysis)
              self.dataframe.to_excel('result.xlsx', index=False)          

obj = Reddit()
obj.main()



              




