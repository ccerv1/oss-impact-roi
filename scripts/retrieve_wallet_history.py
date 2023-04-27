from dotenv import load_dotenv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import shutil
import yaml


load_dotenv()
DOWNLOAD_DIR = os.getenv('LOCAL_PATH')
STORAGE_DIR = "data/ledgers"
SLEEP = 5
MAX_TRIES = 5


def data_already_exists(project_name, wallet_address):

    data_file = f'{STORAGE_DIR}/{project_name}-{wallet_address}.csv'
    return os.path.isfile(data_file)


def download_zerion_history(driver, project_name, wallet_address):

    destination = f'{STORAGE_DIR}/{project_name}-{wallet_address}.csv'
    url = f'https://app.zerion.io/{wallet_address}/history'
    
    driver.get(url)
    print(f"Loading Zerion for {project_name}")
    time.sleep(SLEEP) # wait for page to load    
    try:
        accept_button = driver.find_element(By.XPATH, "//*[contains(text(),'Accept')]/ancestor::button")
        accept_button.click()
        time.sleep(SLEEP) # wait for cookies to be accepted
    except:
        pass

    try:
        button = WebDriverWait(driver, SLEEP*2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Download CSV')]"))
        )
        button.click()
    except:
        print("Zerion appears unable to support analytics for this address:", url)
        return

    notFound = True
    tries = 0
    while notFound:
    
        time.sleep(SLEEP) # wait for download to complete
        tries += 1
        # Find the downloaded file and move it to the correct destination
        downloaded_file = max([os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)], key=os.path.getctime)
        print(downloaded_file)
        if wallet_address.lower() in downloaded_file.lower():
            notFound = False

        if tries == MAX_TRIES:
            print(f"Unable to find a history for {project_name} at {url}.")
            return
    
    shutil.move(downloaded_file, destination)
    print(f"Successfully downloaded Zerion history for {project_name} - {wallet_address} to {destination}.")


def retrieve_wallet_history(project_name, wallet_address, override=False):

    if not override:
        if data_already_exists(project_name, wallet_address):
            print(f"File for {project_name} - {wallet_address} already exists. Skipping download.")
            return

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    download_zerion_history(driver, project_name, wallet_address)
    driver.quit()

if __name__ == '__main__':
    retrieve_wallet_history('Giveth', '0x4D9339dd97db55e3B9bCBE65dE39fF9c04d1C2cd')
