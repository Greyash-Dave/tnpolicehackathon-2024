from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict
import time
import os
from dotenv import load_dotenv
import json

class TwitterScraper:
    def __init__(self):
        load_dotenv()
        self.driver = self.setup_driver()
        
    def setup_driver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def login(self) -> bool:
        try:
            self.driver.get("https://x.com/i/flow/login")
            
            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
            )
            email_input.send_keys(os.getenv("EMAIL"))
            email_input.send_keys(Keys.ENTER)
            
            # Handle potential username verification
            try:
                username_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='ocfEnterTextTextInput']"))
                )
                username_input.send_keys(os.getenv("USER"))
                username_input.send_keys(Keys.ENTER)
            except TimeoutException:
                pass
            
            # Enter password
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
            )
            password_input.send_keys(os.getenv("PASS"))
            password_input.send_keys(Keys.ENTER)
            
            # Verify login success
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='primaryColumn']"))
            )
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def search_and_collect_tweets(self, query: str, max_tweets: int = 5) -> List[Dict]:
        try:
            # Navigate to search
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='SearchBox_Search_Input']"))
            )
            search_input.clear()
            search_input.send_keys(query)
            search_input.send_keys(Keys.ENTER)
            
            # Wait for tweets to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
            )
            
            tweets_data = []
            processed_tweets = set()
            
            while len(tweets_data) < max_tweets:
                # Find all tweet elements
                tweets = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
                
                for tweet in tweets:
                    if len(tweets_data) >= max_tweets:
                        break
                        
                    try:
                        # Get tweet ID
                        tweet_id = tweet.get_attribute("data-tweet-id")
                        if not tweet_id or tweet_id in processed_tweets:
                            continue
                        
                        # Extract tweet text
                        tweet_text_element = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
                        tweet_text = tweet_text_element.text
                        
                        # Extract username
                        username_element = tweet.find_element(By.CSS_SELECTOR, "[data-testid='User-Name']")
                        username = username_element.text.split('\n')[0]
                        
                        # Append tweet data
                        tweets_data.append({
                            'username': username,
                            'text': tweet_text,
                            'tweet_id': tweet_id
                        })
                        processed_tweets.add(tweet_id)
                        
                        print(f"Found tweet: {tweet_text} by {username}")
                        
                    except NoSuchElementException as e:
                        print(f"Error extracting tweet data: {str(e)}")
                        continue
                
                # Scroll down to load more tweets
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new tweets to load
                
                # Check if new tweets are loaded
                new_tweets = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
                if len(new_tweets) == len(tweets):
                    print("No more tweets loaded. Exiting.")
                    break
                    
            return tweets_data
            
        except Exception as e:
            print(f"Error collecting tweets: {str(e)}")
            return []
    
    def close(self):
        self.driver.quit()

def main():
    scraper = TwitterScraper()
    try:
        if scraper.login():
            tweets = scraper.search_and_collect_tweets("#ad #crypto")
            time.sleep(5)
            with open('tweets.json', 'w') as f:
                json.dump(tweets, f, indent=4)
    finally:
        scraper.close()

if __name__ == "__main__":
    main()