import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import shutil
import yaml

DOWNLOAD_DIR = '/Users/cerv1/Dropbox/Hypercerts/oss-impact-roi/'


def download_zerion_history(driver, project_name, wallet_address, override=False):
    destination = f'data/ledgers/{project_name}-{wallet_address}.csv'

    # Check if the file already exists and override is not turned on
    if os.path.exists(destination) and not override:
        print(f"File for {project_name} - {wallet_address} already exists. Skipping download.")
        return

    url = f'https://app.zerion.io/{wallet_address}/history'
    driver.get(url)
    print(f"Loading Zerion for {project_name}")
    time.sleep(5) # wait for page to load    
    try:
        accept_button = driver.find_element(By.XPATH, "//*[contains(text(),'Accept')]/ancestor::button")
        accept_button.click()
        time.sleep(5) # wait for cookies to be accepted
    except:
        pass # cookies popup not found, ignore

    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Download CSV')]"))
    )
    button.click()

    notFound = True
    count = 0
    while notFound:
    
        time.sleep(5) # wait for download to complete
        count += 1
        # Find the downloaded file and move it to the correct destination
        downloaded_file = max([os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)], key=os.path.getctime)
        print(downloaded_file)
        if wallet_address.lower() in downloaded_file.lower():
            notFound = False

        if count == 5:
            print(f"Unable to find a history for {project_name} at {url}.")
            return
    
    shutil.move(downloaded_file, destination)
    print(f"Successfully downloaded Zerion history for {project_name} - {wallet_address} to {destination}.")


def retrieve_wallet_history(project_name, wallet_address, override=False):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    download_zerion_history(driver, project_name, wallet_address, override)
    driver.quit()

if __name__ == '__main__':
    retrieve_wallet_history('Giveth', '0x4D9339dd97db55e3B9bCBE65dE39fF9c04d1C2cd')
