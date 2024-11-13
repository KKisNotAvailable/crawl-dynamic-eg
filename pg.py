from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from tqdm import tqdm
import re
import platform

CUR_SYS  = platform.system()

EXT_DISK = "F:/" if CUR_SYS == 'Windows' else '/Volumes/KINGSTON/'
EXT_DISK += "Homebuilder/"

OLD_FILES = EXT_DISK + "2016_files/"
DATA_PATH = f"{OLD_FILES}processed_data/"
COMSTAT_PATH = f"{OLD_FILES}Compustat/"

VAR_PATH = EXT_DISK + "Variables/"

WEBDRIVER_PATH = "/Users/kyk/Desktop/Misc/edgedriver_arm64/"


def download_median_HH_income(driver, fips = "06037"):
    '''
    Download directly from the path, file will be "MHICA{fips}A052NCEN.csv"
    '''
    # Direct download path (not to the FRED display page)
    addr = f'''https://fred.stlouisfed.org/graph/fredgraph.csv?
    bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&
    graph_bgcolor=%23ffffff&height=450&mode=fred
    &recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=720
    &nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes
    &id=MHICA{fips}A052NCEN&scale=left&cosd=1989-01-01&coed=2022-01-01
    &line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3
    &lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Annual&fam=avg&fgst=lin
    &fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2024-11-13
    &revision_date=2024-11-13&nd=1989-01-01'''

    driver.get(addr)

    # Allow some time for the page to load or download
    time.sleep(1.5)

def download_unemployment(driver, fips = "48039", start_year = "2000"):
    '''
    Need to download files interactively, file will be "file.csv",
    so will rename it directly after download.
    '''
    addr = f"https://data.bls.gov/dataViewer/view/timeseries/LAUCN{fips}0000000004"

    time.sleep(1.5)
    driver.get(addr)

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

    # Wait for the download to complete
    time.sleep(2)

    # 4. Wait until "file.csv" exist in download path, rename it
    new_name = f"unemp_{fips}.csv"


def main():

    # Specify the desired download directory
    download_dir = "/Users/kyk/Desktop/projects/scrapper/"  # Replace with your actual download path

    # Set up Chrome options
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,  # Set download path
        "download.prompt_for_download": False,       # Disable "Save As" prompt
        "download.directory_upgrade": True,          # Allow overwriting files in download folder
        "safebrowsing.enabled": True                 # Enable safe browsing to avoid download blocking
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize the Chrome WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    # download_median_HH_income(driver=driver)
    download_unemployment(driver=driver, fips="06037")

    driver.quit()


if __name__ == '__main__':
    main()


