from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
from tqdm import tqdm
import logging
import re
import platform

CUR_SYS  = platform.system()

EXT_DISK = "F:/" if CUR_SYS == 'Windows' else '/Volumes/KINGSTON/'
EXT_DISK += "Homebuilder/"

OLD_FILES = EXT_DISK + "2016_files/"
DATA_PATH = f"{OLD_FILES}processed_data/"
COMSTAT_PATH = f"{OLD_FILES}Compustat/"

VAR_PATH = EXT_DISK + "Variables/"

def download_median_HH_income(driver, fips, state_abbr):
    '''
    Download directly from the path, file will be "MHICA{fips}A052NCEN.csv"
    '''
    # Direct download path (not to the FRED display page)
    addr = f'''https://fred.stlouisfed.org/graph/fredgraph.csv?
    bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&
    graph_bgcolor=%23ffffff&height=450&mode=fred
    &recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=720
    &nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes
    &id=MHI{state_abbr}{fips}A052NCEN&scale=left&cosd=1989-01-01&coed=2022-01-01
    &line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3
    &lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Annual&fam=avg&fgst=lin
    &fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2024-11-13
    &revision_date=2024-11-13&nd=1989-01-01'''


    # addr = f"https://fred.stlouisfed.org/series/MHI{state_abbr}{fips}A052NCEN"

    driver.get(addr)

    # download_button = driver.find_element(By.ID, "download-button")
    # download_button.click()

    # Allow some time for the page to load or download
    time.sleep(2)

def download_unemployment(driver, down_path, fips = "48039", start_year = "2000"):
    '''
    Need to download files interactively, file will be "file.csv",
    so will rename it directly after download.
    '''
    addr = f"https://data.bls.gov/dataViewer/view/timeseries/LAUCN{fips}0000000004"

    driver.get(addr)

    time.sleep(1.5)

    # 1. Drop down list choose start and end year (but we fix end here)
    dropdown = Select(driver.find_element(By.ID, "dv-start-year"))
    dropdown.select_by_value(str(start_year))

    # 2. Click the update button (page won't refresh after the previous step, so no need to wait)
    update_button = driver.find_element(By.ID, "dv-submit")
    update_button.click()

    time.sleep(2)

    # 3. Click the ".CSV" button to download (wait until clickable or 10 seconds)
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "csvclickLA"))
    )
    download_button.click()

    # 4. Wait until "file.csv" exist in download path, rename it
    while True:
        file_path = os.path.join(down_path, 'file.csv')
        if os.path.exists(file_path):  # Check if the file exists
            new_file_path = os.path.join(down_path, f"unemp_{fips}.csv")
            os.rename(file_path, new_file_path)  # Rename the file
            break

        time.sleep(1)


def batch_download(target: str):
    # Configure logging
    logging.basicConfig(
        filename="failures.log",  # Log file name
        level=logging.ERROR,      # Only log errors
        format="%(message)s"      # Simple message format
    )

    # prep the fips list
    fips_list = pd.read_csv('fips2county.tsv.txt', delimiter='\t', dtype={'CountyFIPS': 'str'})

    # Specify the desired download directory
    download_dir = VAR_PATH + f"{target.lower()}/"

    # Set up Chrome options
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,  # Set download path
        "download.prompt_for_download": False,       # Disable "Save As" prompt
        "download.directory_upgrade": True,          # Allow overwriting files in download folder
        "safebrowsing.enabled": True                 # Enable safe browsing to avoid download blocking
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # to run webdriver in the background (won't show window)
    chrome_options.add_argument("--headless")

    # Initialize the Chrome WebDriver with options
    # driver = webdriver.Chrome(options=chrome_options)

    # TODO: open and close driver in the unemployment, but median HH income can use the same driver

    counter = 5

    for cur_fips, cur_state in tqdm(
        zip(fips_list['CountyFIPS'], fips_list['StateAbbr']),
        total=fips_list.shape[0]
    ):

        try:
            driver = webdriver.Chrome(options=chrome_options)

            counter -= 1
            if target.lower() == 'unemployment':
                download_unemployment(driver=driver, fips=cur_fips, down_path=download_dir)
            elif target.lower() == 'median_hh_income':
                download_median_HH_income(driver=driver, fips=cur_fips, state_abbr=cur_state)

            driver.quit()
            # if counter == 0: return
        except:
            # pass
            logging.error(f"{cur_fips}")

    # driver.quit()


def main():
    batch_download('unemployment')
    # batch_download('median_hh_income')

if __name__ == '__main__':
    main()


