# Cointelegraph Scraper
This is an automation tool to fetch articles data from [cointelgraph.com](https://cointelegraph.com/).
The articles on the homepage of the website are collected and their metadata(including title, author, date, etc.) is saved as output.

# Installation

## Mac OS
1. Install brew from [here](https://brew.sh/).
2. Install `git` and  `pipenv` using brew. 
    ```bash
    brew install git pipenv
    ```
3. Clone this repository. 
    ```bash
    git clone https://github.com/dub-basu/cointelegraph-scraper/
    ```
4. Install the Python dependencies and create a virtual env using the pipfile provided.
    ```bash
    cd cointelegraph-scraper
    pipenv install
    ```
5. Downlaod the Firefox driver for selenium from [here](https://github.com/mozilla/geckodriver/releases). Extract the `tar.gz` file and copy the content to any directory in your `$PATH`.

# Usage
0. Activate the Python environment using pipenv.
    ```bash
    pipenv shell
    ```
## Download new articles
Download new articles from the website is a two step process. 

1. Step 1: Enter the following command replacing the date in the given format YYYY-MM-DD.
    ```bash
    python main.py step1 --date YYYY-MM-DD
    ```
    This will open up a browser instance and keep loading the page till an article is found which was posted before the provided date. 
    All the articles between the current date and the provided date will be download in the form of an `HTML` file(`sources.html` by default).
2. Step 2: Enter the following command replacing the date in the given format YYYY-MM-DD. 
    ```bash
    python main.py step2 --date YYYY-MM-DD
    ```
    This will parse the URLs of articles obtained in HTML file from step 1 and fetch their data one-by-one. 
3. Once completed, the results will be saved in the `downloads` directory in the form of CSV files.

## Updating existing articles data

1. Choose this option if you want to update the data present in a CSV file that was obtained from step 2 above. 
    ```bash
    python main.py update --filepath <path-to-your-csv-file>
    ```
    A new file will be created in the downloads directory.



