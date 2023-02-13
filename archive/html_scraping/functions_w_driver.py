from bs4 import BeautifulSoup
import re
import pandas as pd
from constants import *
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def initialize_webdriver():
    
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)

    return driver


def get_tag_page_soup(tag: str, driver):
    
    url = URL_TAG_BASE + tag

    try:

        html_content = driver.get(url).page_source
        soup = BeautifulSoup(html_content, "html")
        return soup

    except:
        
        print(f"Cannot get page from {tag} tag")

    

def get_tagged_vid_url_list(tag_html_soup, vid_count):

    vid_group_div_attr_dict = {"data-e2e": "challenge-item-list"}
    tagged_vid_attr_dict = {"class":"tiktok-yz6ijl-DivWrapper e1u9v4ua1"}

    tagged_vid_group = tag_html_soup.find("div", attrs=vid_group_div_attr_dict)
    tagged_vids = tagged_vid_group.find_all("div", attrs=tagged_vid_attr_dict)

    vid_urls = []

    for i in range(0, vid_count):
        try:
            vid = tagged_vids[i]
            vid_urls.append(vid.find("a")["href"])

        except IndexError:
            break

    return vid_urls

def get_user_prof_url_from_vid_url(vid_url):
    
    re_pat = "(.+?)\/video\/"

    try:
        prof_url = re.search(re_pat, vid_url).group(1)
        return prof_url

    except:
        print(f"Error shortening {vid_url}")

def get_user_prof_url_list(vid_url_list):

    user_prof_url_list = []

    for url in vid_url_list:
        user_prof_url = get_user_prof_url_from_vid_url(url)
        user_prof_url_list.append(user_prof_url)

    return user_prof_url_list

def get_user_prof_url_list_from_tag(tag, user_prof_count, driver):

    tag_page_soup = get_tag_page_soup(tag, driver)
    tagged_vid_url_list = get_tagged_vid_url_list(tag_page_soup, user_prof_count)
    prof_url_list = get_user_prof_url_list(tagged_vid_url_list)

    return prof_url_list

def scrape_profile_urls_from_tag_dict(tag_dict, driver):
    profile_url_list = []

    for tag in tag_dict:
        count = tag_dict[tag]

        profile_url_list.append(get_user_prof_url_list_from_tag(tag, count, driver))

    # Flatten list
    flat_profile_url_list = list(np.concatenate(profile_url_list).flat)

    # Eliminate duplicates
    deduped_profile_url_list = []
    [deduped_profile_url_list.append(url) for url in flat_profile_url_list if url not in deduped_profile_url_list]

    return deduped_profile_url_list

def get_username_from_profile_url(profile_url):
    
    re_pat = "\/(@.*)"

    try:
        username = re.search(re_pat, profile_url).group(1)
        return username

    except:
        print(f"Error shortening {profile_url}")

def get_username_list_from_profile_url_list(profile_url_list):
    username_list = []

    for profile_url in profile_url_list:
        username = get_username_from_profile_url(profile_url)
        username_list.append(username)

    return username_list

def get_profile_soup_from_profile_url(profile_url, driver):
    html_content = driver.get(profile_url).page_source
    soup = BeautifulSoup(html_content, "html")

    return soup

# For testing
def run_scrape():

    driver = initialize_webdriver()
    tag_dict = {"israel": 20, "ukraine": 20}

    profile_url_list = scrape_profile_urls_from_tag_dict(tag_dict, driver)

    driver.quit

    return profile_url_list