from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from constants import *

def get_tag_page_soup(tag: str):
    
    url = URL_TAG_BASE + tag
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "html")

    return soup

def get_tagged_vid_url_list(tag_html_soup, vid_count):

    vid_group_div_attr_dict = {"data-e2e": "challenge-item-list"}
    tagged_vid_attr_dict = {"class":"tiktok-yz6ijl-DivWrapper e1u9v4ua1"}

    tagged_vid_group = tag_html_soup.find("div", attrs=vid_group_div_attr_dict)
    tagged_vids = tagged_vid_group.find_all("div", attrs=tagged_vid_attr_dict)

    vid_urls = []

    for i in range(0, vid_count):
        vid = tagged_vids[i]
        vid_urls.append(vid.find("a")["href"])

    return vid_urls

def get_prof_url_from_vid_url(vid_url):
    
    re_pat = "(.+?)\/video\/"

    try:
        prof_url = re.search(re_pat, vid_url).group(1)
        return prof_url

    except:
        print(f"Error shortening {vid_url}")

def get_prof_url_list_from_vid_url_list(vid_url_list):

    prof_url_list = []

    for url in vid_url_list:
        user_prof_url = get_prof_url_from_vid_url(url)
        prof_url_list.append(user_prof_url)

    return prof_url_list

def get_prof_url_list_from_tag(tag, user_prof_count):

    tag_page_soup = get_tag_page_soup(tag)
    tagged_vid_url_list = get_tagged_vid_url_list(tag_page_soup, user_prof_count)
    prof_url_list = get_prof_url_list_from_vid_url_list(tagged_vid_url_list)

    return prof_url_list