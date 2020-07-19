import os
from datetime import datetime
import requests
import logging

URL = 'https://cointelegraph.com'
LOGFILE = 'cointelegraph.log'


def get_logger():
    logger = logging.getLogger('ct_logger')
    logger.setLevel('DEBUG')

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)-8s: %(message)s')
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(LOGFILE, mode='a')
    file_formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)-8s: %(message)s',
        "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def string_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def validate_csv_filepath_arg(filepath):
    if filepath is None or not os.path.exists(filepath):
        logger.critical('Invalid CSV file')
        return False
    return True


def validate_date_arg(date_str):
    try:
        if date_str is None:
            logger.critical('No date found')
            return False
        date = string_to_date(date_str)
        if date > datetime.now().date():
            logger.critical(
                'Entered date must not be greater than today\'s date')
            return False
        return True
    except Exception:
        logger.critical('Invalid date')
        return False


def get_html(driver):
    html = driver.page_source
    return html


def write_html(filename, content):
    with open(filename, 'w+') as hf:
        hf.write(content)
        hf.close()


def get_content(url):
    HEADERS = {
       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; \
           rv:73.0) \Gecko/20100101 Firefox/73.0',
    }
    return requests.get(url, headers=HEADERS).text


def is_url_valid(url):
    return url.find('/news') > 0


logger = get_logger()
