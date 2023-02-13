import re
import json
import pandas as pd
import datetime as dt
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os.path

def create_tag_list_from_input():

    print("Input a series of tags followed by *return*. When done, input 0 and press *return*")
    tag_list = []

    while True:
        tag = str(input())
        if tag == "0":
            break

        tag_list.append(tag)

    print()

    return tag_list

def initialize_webdriver(head=False):
    
    try:

        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        if head == False:

            options = Options()
            options.headless = True

            driver = webdriver.Chrome(executable_path=ChromeDriverManager(log_level=0).install(), options=options, desired_capabilities=capabilities)

        else:

            driver = webdriver.Chrome(executable_path=ChromeDriverManager(log_level=0).install(), desired_capabilities=capabilities)

        return driver

    except:
        print("Could not initialize webdriver. Please check your connection")

def get_tag_id_from_log(tag, driver):

    TAG_URL_BASE = "https://www.tiktok.com/tag/"

    tag_url = TAG_URL_BASE + tag
    driver.get(tag_url)

    time.sleep(5)
    log_raw = driver.get_log('performance')

    re_pat = "challengeID=(\d*)"
    tag_id = re.search(re_pat,str(log_raw)).group(1)

    return tag_id

def get_api_url_by_tag(tag, driver, tagged_video_rank_limit=30):

    # Looks like upper limit for tagged_video_rank_limit is 30
    try:
        print(f"Getting tagID for {tag} tag")
        tag_id = get_tag_id_from_log(tag, driver)
        api_url = f"https://us.tiktok.com/api/challenge/item_list/?aid=1988&app_language=en&app_name=tiktok_web&battery_info=0.96&browser_language=en-US&browser_name=Mozilla&browser_online=true&browser_platform=MacIntel&browser_version=5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/99.0.4844.83%20Safari/537.36&challengeID={tag_id}&channel=tiktok_web&cookie_enabled=true&count={str(tagged_video_rank_limit)}&cursor=0&device_id=7079234359529571883&device_platform=web_pc&focus_state=true&from_page=hashtag&history_len=2&is_fullscreen=false&is_page_visible=true&language=en&os=mac&priority_region=&referer=&region=US&screen_height=900&screen_width=1440&tz_name=America/Denver&verifyFp=verify_92ab5e905a0130223decf26be892a2c3&webcast_language=en&msToken=HHlgwHPAXaOOSq_--WCyyQPzzazo91ulJBDO6I7xn-rQFCihjCFy1GrrIrq4hXWYlSjrEw5TYe2bSqNTPIx09q_jaDNW5JKFYu0eHPQg-LfGmjo3Zomw4M9_xJrFwhed36z4PTmVCTKPZbyApg==&X-Bogus=DFSzswROvNhANJqcSROcyR/F6q9d"

        return api_url

    except:
        print(f"Could not access endpoint for {tag}")


def get_tag_json_from_api_url(api_url, tag, driver):
    
    try:

        print(f"Scraping {tag} tag data at API endpoint")
        print()

        driver.get(api_url)
        html_within_pre_tag = driver.find_element_by_tag_name("pre").text
        data = json.loads(html_within_pre_tag)

        return data

    except:
        print(f"Could not retrieve json for {api_url}")

def scrape_tag_ids_from_tag_json(tag_json):
    
    tag_id_dict = {}

    for i in range(0, len(tag_json["itemList"])):

        for j in range(0, len(tag_json["itemList"][i]["textExtra"])):
            path = tag_json["itemList"][i]["textExtra"][j]
            hashtagName = path["hashtagName"]
            hashtagId = path["hashtagId"]

            if hashtagName not in tag_id_dict: 
                tag_id_dict[hashtagName] = hashtagId
            
    return tag_id_dict

def scrape_tag_data_from_tag_json(tag_json, video_rank_limit=30):

    rank_list = []
    username_list = []
    name_list = []
    bio_list = []
    verified_list = []
    video_create_time_list = []
    following_count_list = []
    follower_count_list = []
    video_count_list = []
    heart_count_list = []
    digg_count_list = []

    limit = min(len(tag_json["itemList"]), video_rank_limit)

    for i in range(0, limit):
        
        rank_list.append(str(i))
        username_list.append(tag_json["itemList"][i]["author"]["uniqueId"])
        name_list.append(tag_json["itemList"][i]["author"]["nickname"])
        bio_list.append(tag_json["itemList"][i]["author"]["signature"])
        verified_list.append(tag_json["itemList"][i]["author"]["verified"])

        video_create_time_list.append(tag_json["itemList"][i]["createTime"])

        following_count_list.append(tag_json["itemList"][i]["authorStats"]["followingCount"])
        follower_count_list.append(tag_json["itemList"][i]["authorStats"]["followerCount"])
        video_count_list.append(tag_json["itemList"][i]["authorStats"]["videoCount"])
        heart_count_list.append(tag_json["itemList"][i]["authorStats"]["heartCount"])
        digg_count_list.append(tag_json["itemList"][i]["authorStats"]["diggCount"])

    scraped_data_dict = {
        "username": username_list,
        "name": name_list,
        "bio": bio_list,
        "verified": verified_list,
        "video_create_time": video_create_time_list,
        "following_count": following_count_list, 
        "follower_count": follower_count_list, 
        "video_count": video_count_list, 
        "heart_count": heart_count_list, 
        "digg_count": digg_count_list,
        "rank": rank_list
    }

    scraped_data_df = pd.DataFrame(scraped_data_dict)

    return scraped_data_df

def get_df_from_tag(tag):

    driver = initialize_webdriver()
    api_url = get_api_url_by_tag(tag, driver)

    tag_json = get_tag_json_from_api_url(api_url, tag, driver)
    scrape_time = dt.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    df = scrape_tag_data_from_tag_json(tag_json)

    df["tag"] = tag
    df["scrape_time"] = scrape_time

    return df

def get_df_from_tag_list(tag_list):

    df = get_df_from_tag(tag_list[0])

    for i in range(1, len(tag_list)):
        new_df = get_df_from_tag(tag_list[i])
        df = pd.concat([df, new_df])

    return df

def run_scraper(tag_list):

    df = get_df_from_tag_list(tag_list)

    if os.path.exists("data/scraped_data.csv"):
        df.to_csv("data/scraped_data.csv", mode="a", header=False, index=False)
        print("Appended new data to data/scraped_data.csv")
        print()

    else:
        df.to_csv("data/scraped_data.csv", index=False)
        print("Wrote data/scraped_data.csv")
        print()

def print_title():
    print()
    print("============================")
    print("RUNNING TAGTOK WEBSCRAPER V0")
    print("============================")
    print()