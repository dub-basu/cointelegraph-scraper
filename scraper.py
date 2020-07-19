from time import sleep

from bs4 import BeautifulSoup as bs
from selenium import webdriver

from utils import (URL, get_content, get_html, is_url_valid, logger,
                   string_to_date)


def fetch_and_save(date_string, source_html):
    logger.info('Starting automated browser window. ')
    driver = webdriver.Firefox()
    driver.get(URL)

    accept_cookies(driver)
    sleep(3)
    load_more(driver, date_string)
    html = get_html(driver)

    with open(source_html, 'w') as hf:
        hf.write(html)
        hf.close()
    driver.close()
    logger.info('Step 1 complete')


def accept_cookies(driver):
    accept_button = driver.find_element_by_xpath(
        "//button[@class='btn privacy-policy__accept-btn']")
    logger.debug('Found accept button')
    accept_button.click()
    logger.debug('Clicked accept button')


def get_last_date(driver):
    logger.debug('Trying to find last article on page')

    home_page = bs(get_html(driver), 'html.parser')
    articles_tags = home_page.find(
        'ul', {'class': 'posts-listing__list'}).find_all('article')

    last_index = -1
    while not is_url_valid(URL + articles_tags[last_index].header.a['href']):
        last_index -= 1

    url = URL + articles_tags[last_index].header.a['href']
    logger.debug('Found last article element')

    logger.debug('Fetching last article data from url: [{}]'.format(url))
    article_div = bs(get_content(url), 'html.parser').body.main.find(
        'div', {'class': 'post post-page__article'})
    date = article_div.find(
        'div', {'class': 'post-meta__publish-date'}).time['datetime']
    logger.debug('Extracted date from last article [{}]'.format(str(date)))

    return date


def load_more(driver, date_limit=None):

    date_limit = string_to_date(date_limit)
    logger.debug('Will now load more articles. Date limit: ' + str(date_limit))

    while True:

        last_article_date = string_to_date(get_last_date(driver))
        logger.debug('Last article date = ' + str(last_article_date))

        if last_article_date < date_limit:
            logger.debug('Article too old. Not loading any more articles')
            break
        else:
            logger.debug('Article under limit. Loading more articles')
            load_more_button = driver.find_element_by_xpath(
                "//button[@class='btn posts-listing__more-btn']")
            logger.debug("Found load more button")
            load_more_button.click()
            logger.debug('Pressed load more button')
            sleep(4)
