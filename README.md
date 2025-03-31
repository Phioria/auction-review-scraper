## auction-review-scraper

This python script uses a chrome webdriver through selinium to scrape user reviews of auction companies on the site [liveauctioneers.com](https://liveauctioneers.com).

The script expects a chrome webdriver to be present in the same directory as the python files. Current webdrivers can be downloaded [here](https://googlechromelabs.github.io/chrome-for-testing/).

### Usage

Default usage is currently setup to scrape reviews for the auction company Bidhaus. These reviews are written to a timestamped csv file.

`python main.py`

To modify the company being scraped, just edit main.py with the relevant company info. Company names and codes can be found at liveauctioneers.com.
