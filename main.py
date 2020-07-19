from argparse import ArgumentParser

from parser import ArticleParser
from scraper import fetch_and_save
from utils import logger, validate_csv_filepath_arg, validate_date_arg

SOURCE_FILE = 'source.html'


def step1(date_str):
    fetch_and_save(date_str, SOURCE_FILE)


def step2(date_str):
    parser = ArticleParser.from_html(SOURCE_FILE)
    parser.fetch_artices()
    # parser.articles_to_csv()


def update(csv_filepath):
    logger.info('UPDATE MODE')
    logger.info(
        'Will start to update article from [{}] now'.format(csv_filepath))
    parser = ArticleParser.from_csv(csv_filepath)
    parser.fetch_artices()
    # parser.articles_to_csv()


if __name__ == '__main__':
    logger.info('####### STARTING COINTELEGRAPH SCRAPER #######')

    choices = {'step1': step1, 'step2': step2, 'update': update}
    parser = ArgumentParser(description='Parse data from cointelegraph.com')
    parser.add_argument('step', choices=choices, help='which step to run')
    parser.add_argument('--date', metavar='DATE', type=str, help='DATE limit')
    parser.add_argument(
        '--filepath', metavar='FILEPATH', type=str, help='CSV file')
    args = parser.parse_args()

    function = choices[args.step]
    date, csv_filepath = args.date, args.filepath

    try:
        if function == update and validate_csv_filepath_arg(csv_filepath):
            function(csv_filepath)
        elif function in [step1, step2] and validate_date_arg(date):
            function(date)
    except Exception:
        logger.critical('Failed unexpectedly. Check logs.')
        logger.exception('Exception occured')
