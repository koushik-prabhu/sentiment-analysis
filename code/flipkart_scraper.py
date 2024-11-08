from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd


class FlipkartScraper:

    def __init__(self):
        self.base_url = "https://www.flipkart.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # create an instance of ChromeOptions
        chrome_options = Options()
        # add the headless option
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")

        # Set up the ChromeDriver with the options
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # keep track of review pages
        self.counter = 0

        
    def scraping(self, phone, address, reviews_map):

        self.counter += 1
        if self.counter == 2:
            return reviews_map
        
        print(f'Processing page {self.counter}')
        wait = WebDriverWait(self.driver, 10)
        self.driver.get(address)
        # waiting until phone picture is loaded
        # this also helps to load all the js code first, so that js is not visible in the source code
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="container"]/div/div[3]/div/div/div[1]/div[1]/div/a/div/div/div/img')))
        time.sleep(5)
        # getting the source code of the page
        content = self.driver.page_source
        soup = BeautifulSoup(content, 'html5lib')

        # fetching all the main divs of reviews section
        cards = soup.find_all('div', class_ = 'cPHDOP col-12-12')
        for card in cards:
            # some divs of specirfied class does not represent reviews, discard them
            if card.p != None:
                title = card.p.text
                reviews_map['title'].append(title)
                review_container = card.find('div', class_ ='ZmyHeo')
                review = review_container.div.div.text
                reviews_map['review'].append(review)

        # once the reviews are fetched, head to the next page
        next_button = self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[3]/div/div/div[2]/div[13]/div/div/nav/a[11]')
        # for last page, next button is disabled
        if next_button.is_enabled():
            next_page_url_element = soup.find_all('a', class_ = '_9QVEpD')
            next_page_url_element = next_page_url_element[-1]
            next_page_url = self.base_url + next_page_url_element.get('href')
            # recursive call
            self.scraping(phone, next_page_url, reviews_map)
        else:
            return reviews_map
        

    def process(self):

        reviews_map = { 
            "title" : [],
            "review" : []
        }

        map = {
            "iphone" : 'https://www.flipkart.com/apple-iphone-15-black-128-gb/product-reviews/itm6ac6485515ae4?pid=MOBGTAGPTB3VS24W&lid=LSTMOBGTAGPTB3VS24WVZNSC6&marketplace=FLIPKART'
        }

        for phone, address in map.items():
            self.scraping(phone, address, reviews_map)
            reviews_map['phone'] = phone
            reviews_map['data source'] = 'flipkart'
            print(len(reviews_map['title']))
            print(len(reviews_map['review']))
            dataframe = pd.DataFrame(reviews_map)
            # dataframe.to_csv('flipkart_reviews.csv')

        return dataframe


