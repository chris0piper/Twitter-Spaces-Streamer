

from typing import Dict, List
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from random import randint
import json
import requests


import importlib  
speaker_lookup = importlib.import_module("Twitter-Spaces-Speaker-Lookup.speaker_lookup")
ts = speaker_lookup.Twitter_Spaces()


def transcribe_space(spaces_id):

    print('New space: {}!'.format(spaces_id))
    # set up webdriver
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.headless = True

    driver = webdriver.Chrome(desired_capabilities=caps,options=options)


    # go to the twitch stream
    driver.get("https://twitter.com/i/spaces/{}".format(spaces_id))

    # click to join the stream
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Listen live']"))).click()

    # driver.implicitly_wait(10)
    sleep(5)

    # Iterate through the logs and print the URL of any request containing 'chunk_'
    def process_browser_log_entry(entry):
        response = json.loads(entry['message'])['message']
        return response

    while True:
        browser_log = driver.get_log('performance') 
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'params' in event and 'response' in event['params'] and 'url' in event['params']['response'] and 'chunk_' in event['params']['response']['url']]


        hit_urls = []

        # Open the file in 'ab' (append binary) mode
        with open('audio{}.aac'.format(spaces_id), 'ab') as f:
            for event in events:

                # Skip duplicate urls
                url = event['params']['response']['url']
                if(url in hit_urls):
                    continue

                # Send a GET request to the URL
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code == 200:
                    # Write the content of the response to the file
                    f.write(response.content)
                    hit_urls.append(url)
                else:
                    print("Error downloading file")
        sleep(5)


ts.monitor_user_for_spaces("elon2doge", transcribe_space)
