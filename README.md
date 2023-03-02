
# Google Maps Scraper for Company Details  
A python script to scrape company details from google maps using keyword search.


<!-- ABOUT THE SCRAPER -->
## About The Scraper

This project is for extract company names, sub-names, address and website from a google map for a keyword search, with or without multithreading, using requests, regex, python and selenium.

The script takes search-keyword from the `input.xlsx` file, and save the output in the `output.xlsx` file.

The script also use multithreading for extract data from the web pages faster.

The script uses selenium (google chrome) for get more data from the web pages, because some web pages use javascript to show the data. 

You can setup the number of threads in the `.env` file (see the `THREADS` variable).

### Built With
<div>
<a href="https://www.python.org/">
  <img src="https://cdn.svgporn.com/logos/python.svg" width="50" alt="python" title="python">
</a>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* [Google chrome](https://www.google.com/intl/es-419/chrome/)
* [Python >=3.10](https://www.python.org/)
* [Git]

### Installation

1. Clone the repo
   ```sh
   git clone 
   ```
1. Install python packages (opening a terminal in the project folder)
   ```sh
   python -m pip install -r requirements.txt 
   ```

<!-- USAGE EXAMPLES WITHOUT MULTITHREADING-->
## Usage

1. Set your option in the file `.env`
2. Put the search keyword in the `input.xlsx` file
3. Run the project folder with python: 
    ```sh
    python __main__.py
    ```
4. Wait until the script finish, and check the `output.xlsx` file in the project folder

<!-- USAGE EXAMPLES WITH MULTITHREADING-->
## Usage

1. Set your option in the file `.env`. Set THREADS variable in the file `.env`(Number of process to use for extract at the same time.). By default, no. of threads is 3.
2. Put the search keyword in the `input.xlsx` file
3. Run the project folder with python: 
    ```sh
    python file_parse.py
    ```
4. Wait until the script finish, and check the `output.xlsx` file in the project folder
file_parse.py
<!-- ROADMAP -->
## Roadmap

- [x] Extract company-name, address, sub_name and address for keyword search in google map using selenium
- [x] Multithreading
- [x] `.env` file fro options

<!-- CONTACT -->
## Contact

Neetu Kushwaha - neetumits@gmail.com or nkushwaha@turing.ac.uk

Link: 

## Options

### Show browser during an scraping

Add headless argument in WebScraping object.
```
# WebScraping(headless=True, web_page=web_page)  # show browser or not
```

### Change output filename

You can change it in `def write_to_xlsx`

```
df.to_excel('what_you_like.xlsx')
```

### Scroll slower (problem with Google or network limits)
Add time function
```
time.sleep(your_new_time_in_seconds)
```
# OXSFG-Waste-Water-Treatment-Plant
