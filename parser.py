import csv
import os
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup as bs

from utils import (URL, get_content, is_url_valid, logger, string_to_date)


@dataclass
class Article:
    url: str
    title: str
    author: str
    views: int
    shares: int
    date: str
    diff: str
    tags: list


class ArticleParser:
    """ STEP 2 of Cointelegraph scraping.
    Takes input in the form of either
    a) HTML file:   SOURCE_FILE('source.html' by default) obtained from STEP 1
    b) CSV file:    Path of CSV file obtained after STEP 2. To get updated
                    information for articles in the CSV
    Parses all article URLs from the HTML/CSV file and scrapes article date
    from each URL.
    Generates results.csv in DOWNLOADS_DIR
    """

    DOWNLOADS_DIR = 'downloads'
    CSV_FILE = 'result.csv'

    def __init__(self, urls):
        self.create_directory()
        self.urls = urls
        self.all_urls = self.urls.copy()
        self.validate_urls()

        self.write_urls_to_csv()
        logger.debug('Found [{}] URLs'.format(len(self.urls)))

    @classmethod
    def from_csv(cls, csv_filepath):
        logger.debug(
            'Collecting data from CSV file: [{}]'.format(csv_filepath))
        return cls(ArticleParser.get_urls_from_csv(csv_filepath))

    @classmethod
    def from_html(cls, html_filepath):
        logger.debug(
            'Collecting data from HTML file: [{}]'.format(html_filepath))
        return cls(ArticleParser.get_urls_from_html(html_filepath))

    @staticmethod
    def get_urls_from_csv(csv_filepath):
        with open(csv_filepath, 'r') as csv_file:
            logger.debug('Read CSV file')
            article_urls = [row['url'] for row in csv.DictReader(csv_file)]
            logger.debug('Extracted URLs')

            return article_urls

    @staticmethod
    def get_urls_from_html(html_filepath):
        logger.debug('Reading HTML')
        with open(html_filepath, 'r') as html_file:
            home_page = html_file.read()
            logger.debug('Read HTML file')

            logger.debug('Extracting article tags')
            articles_tags = ArticleParser.get_article_tags_from_page(home_page)
            logger.debug('Article tags extracted')

            article_urls = [ArticleParser.url_from_article_tag(
                tag) for tag in articles_tags]
            logger.debug('Fetched article URLs')

            return article_urls

    @staticmethod
    def get_article_tags_from_page(page_content):
        page = bs(page_content, 'html.parser')
        return page.find('ul', {
            'class': 'posts-listing__list'}).find_all('article')

    @staticmethod
    def url_from_article_tag(article_tag):
        return (URL + str(article_tag.header.a['href']))

    @staticmethod
    def get_article_obj_from_url(url):
        logger.debug('Fetching content from url: [{}]'.format(url))
        article_page_content = get_content(url)
        logger.debug('Fetched article page')

        article_div = bs(article_page_content, 'html.parser').body.find(
            'main').div.div.div.div.div.div.article
        logger.debug('Parsed article tag')

        # For debugging
        # write_html('tmp.html', str(article_div))

        title = article_div.find('h1').string.strip()
        logger.debug('Fetched title: [{}]'.format(title))

        author = article_div.find(
            'div', {'class': 'post-meta__author-name'}).string.strip()
        logger.debug('Fetched author: [{}]'.format(author))

        date_tag = article_div.find(
            'div', {'class': 'post-meta__publish-date'}).time
        date = date_tag['datetime']
        diff = date_tag.string.strip()
        logger.debug('Fetched date: [{}] and diff: [{}]'.format(date, diff))

        stats_div = article_div.find(
            'div', {
                'class': 'post-actions post__block post__block_post-actions'})
        views = -1
        shares = -1
        for div in stats_div.find_all(
            'div', {'class': 'post-actions__item post-actions__item_stat'}):
            name = div.find(
                'span',
                {'class': 'post-actions__item-title'}).string.strip().lower()
            number = int(
                div.find(
                    'span',
                    {'class': 'post-actions__item-count'}).string.strip())
            if name.find('views') > -1:
                views = number
            else:
                shares = number
        logger.debug(
            'Fetched views: [{}] and shares [{}]'.format(views, shares))

        tags_div = article_div.find(
            'ul', {'class': 'tags-list__list'}).find_all('li')
        tags = [tag.a.string.strip() for tag in tags_div]
        logger.debug('Fetched tags: [{}]'.format(tags))

        return Article(url, title, author, views, shares, date, diff, tags)

    @staticmethod
    def write_articles_to_csv(filename, articles):
        """ Writes article objects to a csv file `filename` """
        headers_row = ['url', 'title', 'author',
                       'views', 'shares', 'date', 'diff', 'tags']
        with open(filename, 'w+', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, headers_row, delimiter=',')
            writer.writeheader()
            articles_serialised = [article.__dict__ for article in articles]
            writer.writerows(articles_serialised)

    def write_urls_to_csv(self):
        logger.debug('Writing URLs to CSV')
        headers_row = ['valid_url', 'invalid_urls']
        urls_filepath = os.path.join(self.directory, 'urls.csv')
        with open(urls_filepath, 'w+') as csv_file:
            writer = csv.writer(csv_file, headers_row, delimiter=',')
            writer.writerow(headers_row)
            for url in self.all_urls:
                writer.writerow([
                    url, 'valid' if url in self.urls else 'invalid'])
        logger.debug('Finished writing URLs to CSV')

    def create_directory(self):
        logger.debug('Creating directory')
        directory_name = 'resources_'+datetime.now().strftime('%d-%m-%Y-%H-%M')
        self.directory = os.path.join(self.DOWNLOADS_DIR, directory_name)
        os.makedirs(self.directory, exist_ok=True)
        logger.debug('Created directories successfully')

    def create_result_csv(self):
        logger.debug('Creating result CSV file')
        headers_row = ['url', 'title', 'author',
                       'views', 'shares', 'date', 'diff', 'tags']
        csv_filename = os.path.join(self.directory, self.CSV_FILE)

        self.csv_file = open(csv_filename, 'w')
        self.writer = csv.DictWriter(self.csv_file, headers_row, delimiter=',')
        self.writer.writeheader()

        logger.debug('Result csv file created')

    def fetch_artices(self, date_limit=None):
        self.create_result_csv()
        if date_limit is None:
            date_limit = '1970-01-01'
        logger.debug('Fetching articles data')
        self.articles = []
        for counter, url in enumerate(self.urls):
            logger.info(
                'Fetching article {}/{}'.format(counter+1, len(self.urls)))
            article = ArticleParser.get_article_obj_from_url(url)
            if string_to_date(article.date) >= string_to_date(date_limit):
                self.add_article(article, True)
            else:
                logger.info(
                    'Stopped fetching as articles too old')
                break
            print('..')
        self.csv_file.close()

    def add_article(self, article, add_to_file=True):
        self.articles.append(article)
        if add_to_file:
            self.writer.writerow(article.__dict__)
            self.csv_file.flush()
        logger.debug('Article added')

    def articles_to_csv(self):
        """ Writes articles to file in bulk. """
        csv_filename = os.path.join(self.directory, self.CSV_FILE)
        ArticleParser.write_articles_to_csv(csv_filename, self.articles)

    def validate_urls(self):
        logger.debug('Validating URLs')
        self.urls = list(filter(is_url_valid, self.urls))
        logger.debug('URL validation complete')
