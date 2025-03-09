from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import glob
from datetime import datetime

def setup_driver():
    """Setup and configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def navigate_to_website(driver):
    url = "https://plvr.land.moi.gov.tw/DownloadOpenData"
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    handles = driver.window_handles
    driver.switch_to.window(handles[-1])
    driver.close()
    driver.switch_to.window(handles[0])
    
    history_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "非本期下載"))
    )
    history_link.click()

def click_all_downloads(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "i_download"))
    )
    
    download_elements = driver.find_elements(By.CLASS_NAME, "i_download")
    
    for download in download_elements:
        download.click()
        time.sleep(2)

def download_historical_data(driver):
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "historySeason_id"))
    )
    
    options = select_element.find_elements(By.TAG_NAME, "option")

    format_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "fileFormatId"))
    )
    format_select.click()
    csv_option = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#fileFormatId option[value='csv']"))
    )
    csv_option.click()
    time.sleep(1)

    for option in options:
        season_name = option.text.strip()
        option.click()
        time.sleep(1)    
        
        download_button = driver.find_element(By.ID, "downloadBtnId")
        download_button.click()
        
        # Wait for download to complete
        time.sleep(5)
        
        # Get the download directory (adjust as needed)
        download_dir = os.path.expanduser("~/Downloads")
        
        # Find the most recently downloaded file
        list_of_files = glob.glob(f"{download_dir}/*.zip")
        latest_file = max(list_of_files, key=os.path.getctime)
        
        # Create new filename with the season name
        new_filename = os.path.join(download_dir, f"property_data_{season_name}.zip")
        
        # Rename the file
        os.rename(latest_file, new_filename)
        print(f"Downloaded and renamed: {new_filename}")
        
        time.sleep(3)

def main():
    driver = setup_driver()
    navigate_to_website(driver)
    time.sleep(3)
    click_all_downloads(driver)
    download_historical_data(driver)
    time.sleep(1)  
    driver.quit()

if __name__ == "__main__":
    main()
