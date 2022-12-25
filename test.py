# Microsoft Careers Scraper
# Author: @shubhtoy
# Date: 10/10/2021
# Version: 1.0
# Description: This script scrapes all the Indian jobs from Microsoft Careers website and stores them in a json file.
#             It also scrapes the job description of all the jobs and stores them in a json file.


# Importing Libraries
from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
import json


# Base Urls
url = "https://careers.microsoft.com/us/en/search-results?rt=university?region=in"
url2 = "https://careers.microsoft.com/us/en/search-results?from={no}&s=1"

# Global Variables
driver = ""
all_jobs = {}
list = []
total_pages = 0

# CONFIG
OUTPUT_FILE = "microsoft_jobs.json"
HEADLESS = True


# Headless
options = Options()
if HEADLESS:
    options.add_argument("--headless")


def sel(url):
    global driver
    driver = Chrome(options=options)
    timeout = 10
    driver.get(url)
    # return driver
    element = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/div[2]/div[2]/div/div[2]/div[2]/section/div/div/div[3]/div[1]/div/ul/li[7]",
            )
        )
    )

    return driver


def get_indian_jobs(content):
    # print(content)
    soup = BeautifulSoup(content, features="lxml")
    my_items = soup.find_all("li", {"class": "jobs-list-item"})
    for i in my_items:
        check_location = i.find("span", {"class": "job-location"}).text
        # driver=sel()
        # print(check_location.strip())
        if "India" in check_location:
            # print(check_location)
            # print("-----------------------------------------------------------------------------------------------------------------")
            job_title = i.find("span", {"class": "job-title"}).text.strip()
            job_category = i.find("span", {"class": "job-category"}).text.strip()
            job_date = i.find("span", {"class": "job-date au-target"}).text.strip()
            job_worksite = i.find("span", {"class": "job-worksite"}).text.strip()
            job_link = i.find("a", {"class": "au-target"})["href"]
            all_jobs[job_title] = {
                "job_category": job_category,
                "job_date": job_date,
                "job_worksite": job_worksite,
                "job_link": job_link,
            }

    # print(all_jobs)
    # print(len(all_jobs.keys()))


def get_pages():
    for i in range(1, total_pages):

        try:
            driver.get(url2.format(no=i * 20))
            time.sleep(2)
            get_indian_jobs(driver.page_source)
        except:
            time.sleep(10)
            driver.get(url2.format(no=i * 20))
            get_indian_jobs(driver.page_source)


def get_job_data(job_json):
    driver.get(job_json["job_link"])
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, features="lxml")

    job_no = soup.find(
        "span",
        {
            "data-ph-id": "ph-view1-external-1669028214471-ph-job-details-v1e39swx-YQw6Fm"
        },
    ).text
    date_posted = soup.find(
        "span",
        {
            "data-ph-id": "ph-view1-external-1669028214471-ph-job-details-v1e39swx-FGRbGq"
        },
    ).text
    travel = soup.find(
        "span",
        {
            "data-ph-id": "ph-view1-external-1669028214471-ph-job-details-v1e39swx-imrLpV"
        },
    ).text.strip()
    role_type = soup.find(
        "span",
        {
            "data-ph-id": "ph-view1-external-1669028214471-ph-job-details-v1e39swx-eY0IJF"
        },
    ).text
    employment_type = soup.find(
        "span",
        {
            "data-ph-id": "ph-view1-external-1669028214471-ph-job-details-v1e39swx-s9qAcP"
        },
    ).text

    job_dec = soup.find_all("p", {"style": "margin: 0px;"})
    for i in job_dec:
        texts = i.find_all(text=True)
        list.append(texts[0] if len(texts) > 0 and texts[0] != "\xa0" else "")

    list = [i for i in list if i != ""]

    all_job_data = "\n".join(list)

    job_json["job_no"] = job_no
    job_json["date_posted"] = date_posted
    job_json["travel"] = travel
    job_json["role_type"] = role_type
    job_json["employment_type"] = employment_type
    job_json["job_dec"] = all_job_data

    return job_json


def main():
    print("--Starting Script--")
    driver = sel(url)
    soup = BeautifulSoup(
        driver.page_source, features="lxml"
    )  # If this line causes an error, run 'pip install html5lib' or install html5lib
    get_indian_jobs(driver.page_source)
    print("--Getting Total Pages--")
    no_of_jobs = soup.find("span", {"class": "total-jobs"}).text
    print(no_of_jobs)
    total_pages = int(no_of_jobs) // 20
    print(total_pages)
    print("--Total Pages--> " + str(total_pages))
    print("--Getting Indian Jobs--")

    get_pages()

    print("--Total Indian Jobs--> " + str(len(all_jobs.keys())))

    print("--Getting Job Data--")

    for i in all_jobs.keys():
        print("--Getting Job Data for Job No--> " + i)
        all_jobs[i] = get_job_data(all_jobs[i])
        # print(all_jobs[i])

    # Changing Format of json
    new_json = {}
    new_json["Company"] = "Microsoft"
    new_json["Career Page"] = url
    new_json["data"] = []

    for i, j in all_jobs.items():
        j["job_title"] = i
        new_json["data"].append(j)

    all_jobs = new_json

    print("--Writing to Json--")
    # dict to json
    with open(OUTPUT_FILE, "w") as fp:
        json.dump(all_jobs, fp, indent=4)

    print("--Closing Driver--")
    driver.close()
    print("--Script Ended--")
