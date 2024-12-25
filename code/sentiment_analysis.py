import pandas as pd
from flipkart_scraper import FlipkartScraper
from reddit_fetcher import RedditFetcher
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import s3fs
import os
from datetime import datetime

#code check 1.1

class SentimentAnalysis:

    def __init__(self):
        pass


    def process(self):

        #creating objects of data source classes
        object1 = FlipkartScraper()
        object2 = RedditFetcher()

        print('Excecuting flipkart web scrape script...')
        df1 = object1.process()
        print('Web scrape script completed it\'s excecution!')
        print('Excecuting reddit api script...')
        df2 = object2.data_extraction()
        print('Reddit api script completed it\'s excecution!')
        #concatinating before pre processing
        dataframe = pd.concat([df1, df2])

        #preprcoessing the reviews
        # dataframe = pd.read_csv('flipkart_reviews.csv')
        dataframe['title'] = dataframe['title'].apply(self.data_cleaning)
        dataframe['review'] = dataframe['review'].apply(self.data_cleaning)
        print('Data cleaning completed')
        # Apply sentiment analysis
        dataframe['sentiment'] = dataframe['review'].apply(self.sentiment_analyzer)
        print('Analyzing the sentiments of the text')
        # dataframe.to_csv('result.csv', index=False)
        self.upload_to_s3(dataframe)

    

    def data_cleaning(self, text):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text) # apart from text, numbers and spaces
        text = re.sub(r'\s+', ' ', text)  # removes extra spaces
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # hyperlinks
        return text
    
    def sentiment_analyzer(self, text):
        # Initialize the VADER sentiment analyzer

        texts = ['not good', 'very good']
        sia = SentimentIntensityAnalyzer()

        for text in texts:
            sentiment_scores = sia.polarity_scores(text)
            compound_score = sentiment_scores['compound']  # 'compound' gives an overall sentiment score
            if compound_score >= 0.05:
                return 1  # Positive sentiment
            elif compound_score <= -0.05:
                return -1  # Negative sentiment
            else:
                return 0  # Neutral sentiment
            
    def upload_to_s3(self, dataframe):
        # Manually configure AWS credentials within the script
        aws_access_key_id = os.environ.get('aws_access_key_id')
        aws_secret_access_key = os.environ.get('aws_secret_access_key')
        if not aws_access_key_id and aws_secret_access_key:
            print('AWS cred is not set')
        aws_region = 'ap-south-1'  # Specify your region
        bucket = 'koushik-sentiment-analysis'
        now = datetime.now()
        date = now.strftime("%d-%m-%Y %H:%M:%S")
        object_key = fr'incoming/output-{date}.csv'

        # Create an S3 file system object using s3fs
        fs = s3fs.S3FileSystem(
            key=aws_access_key_id,
            secret=aws_secret_access_key,
            client_kwargs={'region_name': aws_region}
        )

        # Open the S3 object for writing
        with fs.open(f'{bucket}/{object_key}', 'w') as f:
            # Use the 'to_csv' method of pandas, passing the S3 file object
            dataframe.to_csv(f, index=False) 
        


if __name__ == '__main__':
    obj = SentimentAnalysis()
    obj.process()
    print('Sentiment analysis completed!')