import praw
import pandas as pd
import re
import nltk

class RedditFetcher:
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
    
        subreddits = {
            'Iphone' : ['Iphone 15', 'iphone 15', 'iphone15'],
        }
        reviews = []
        for subreddit, keywords in subreddits.items():
            # retriving subreddit info but only when keywords are matched
            for post in self.reddit.subreddit(subreddit).search(' OR '.join(keywords)):
                try:
                    reviews.append({
                            "phone": keywords[0],
                            "title": post.title,
                            "review": post.selftext
                    })
                except Exception:
                    print('exception occured!')

        dataframe = pd.DataFrame(reviews)
        dataframe['data source'] = 'reddit'

        return dataframe
