# Web Scraper Python

Web scraper in Python for CSE 7337. This scraper has different spiders used to gather different information around the class site

## Tools

This scraper was built using `Scrapy`, which is a Python library to with helper functions for scrapers.

## Instalation (MacOS Instructions)

* Make sure you have `Python` installed
* Install Scrapy

```
pip install scrapy
```

_Note: I had trouble with regular installation so I had to run the following:_

```
sudo pip install scrapy
```

* Install NLTK

```
sudo pip install -U nlt
```

* Download stop words list

```
python
>>> import nltk
>>> nltk.download('stopwords')
```

* Clone project

```
git clone https://github.com/AlexHenkel/WebScraper.git
cd WebScraper
```

## Running spiders

1.  **General spider with all data generated**. See `all_data.csv` to see compiled results.

```
scrapy crawl fmoore -o - > allData.csv -t csv
```

2.  **Term frequency spider**. See `term_frequency.csv` to see compiled results, and `TermFrequencyMatrix.xlsx` to see analyzed resutls.

```
scrapy crawl fmoore-tf -o - > term_frequency.csv -t csv
```

3.  **Graphic links spider**. See `graphic_links.csv` to see compiled results.

```
scrapy crawl fmoore-graphic -o - > graphic_links.csv -t csv
```

4.  **Broken links spider**. See `broken_links.csv` to see compiled results.

```
scrapy crawl fmoore-broken -o - > broken_links.csv -t csv
```

5.  **Duplicate files spider**. See `duplicates.csv` to see compiled results.

```
scrapy crawl fmoore-duplicates -o - > duplicates.csv -t csv
```

6.  **Out-going files spider**. See `outlinks_links.csv` to see compiled results.

```
scrapy crawl fmoore-outlinks -o - > outlinks_links.csv -t csv
```

## Custom settings

To add any of the following settings, append them to any command with the following syntax: `-s SETTING_NAME=<VALUE>`. Each setting should be preceded by `-s` flag.

Example:

```
scrapy crawl fmoore -o - > allData.csv -t csv -s PAGE_LIMIT=10 -s STOP_WORDS='and,the,we,you'
```

* **PAGE_LIMIT**: Limit the number of pages to crawl. Value must be a valid integer
* **STOP_WORDS**: List of words to be considered as stop words, and therefore ignored by the crawler. Value should be a string with values separated by commas and no spaces between. Ex: `'and,the,we,you'`
