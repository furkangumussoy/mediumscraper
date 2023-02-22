import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class MediumScraper:
    def __init__(self, tag):
        self.tag = tag
        self.base_url = 'https://medium.com'
        self.driver = None
        self.data = []

    def start_driver(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()

    def load_page(self, url):
        self.driver.get(url)
        time.sleep(3)

    def scrape_articles(self):
        url = f'{self.base_url}/tag/{self.tag}/latest'
        self.load_page(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('div', class_='js-block')
        for article in articles:
            title = article.find('h3').text.strip()
            author = article.find('a', class_='ds-link').text.strip()
            date = article.find('time')['datetime']
            url = self.base_url + article.find('a', href=re.compile('^/.*$'))['href']
            content = self.scrape_article_content(url)
            self.data.append({'Title': title, 'Author': author, 'Date': date, 'URL': url, 'Content': content})

    def scrape_article_content(self, url):
        self.load_page(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find('div', class_='postArticle-content')
        if content is None:
            print(f'No content found for URL {url}')
            return ''
        return content.text.strip()

    def save_to_csv(self, file_name):
        if not self.data:
            print('No data to save')
            return
        df = pd.DataFrame(self.data)
        try:
            df.to_csv(file_name, index=False)
            print(f'Scraped articles have been saved to {file_name}')
        except Exception as e:
            print(f'Error saving data to CSV file: {e}')

if __name__ == '__main__':
    tag = input("Enter the article tag you want to scrape from Medium: ")
    while not tag:
        tag = input("Invalid input. Please enter a tag: ")
    scraper = MediumScraper(tag)
    scraper.start_driver()
    scraper.scrape_articles()
    scraper.stop_driver()
    file_name = f'medium_{tag}_articles.csv'
    scraper.save_to_csv(file_name)
