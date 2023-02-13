# TikTok Tag-to-Profile Scraper

## Overview
This program scrapes TikTok for user profile data via its API. 

On the TikTok website, one can find the most popular videos labeled with a hashtag {tag} with the URL: https://www.tiktok.com/tag/{tag}. Thumbnails of the videos are listed in order of popularity (from left-to-right, then from up-to-down). 

Given a tag, this program accesses an API endpoint that corresponds with the above webpage. The endpoint JSON contains detailed information about each listed video and the users that posted them. This program scrapes the relevant information and metadata, stores it in a Pandas Dataframe, and exports it to a csv file. If the csv file already exists, it appends the new data.

## API endpoint generation
I originally found the API endpoint associated with tag {tag} by inspecting network activity on the page https://www.tiktok.com/tag/{tag}. After some tinkering, I found that the "challengeID" field in the endpoint's URL corresponded uniquely to {tag}. 

The program generates a URL by modifying this URL's "challengeID" field. Given a tag {tag}, the program finds its corresponding "challengeID" via the following process:
* Using Selenium and a webdriver for Chrome, navigate to https://www.tiktok.com/tag/{tag}
* Wait 5 seconds for the page to load
* Retrieve the webdriver's performance log
* Extract the "challengeID" value from the request headers data within the raw performance log"

The program builds the API endpoint URL corresponding to {tag} with its challengeID. It then scrapes it.

The motivation for this roundabout process is to avoid the CAPTCHAs that appear on TikTok when scraping with an automated browser. The CAPTCHAs make it much more inconvenient to scrape the raw html on the https://www.tiktok.com/tag/{tag} page.

## How to use
* Navigate to directory "tag_tok_scraper" on Command Line
* Run: python run_scraper.py 
* Follow instructions to input a series of tags you wish to scrape
* Wait for program to scrape data
* Enter another series of tags if you wish
* To see stored data in csv, run: python see_data.py
* To clear the csv, run: bash clear_data.sh