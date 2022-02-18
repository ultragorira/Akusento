from selenium import webdriver
from selenium.common.exceptions import *
import os
import time
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from functions import move_files, remove_files
from paths import QA_Files
from pathlib import Path
import chromedriver_autoinstaller

JSON_creds = 'Bot_Creds.json'
work_sheet = 'Sheet1'
QA_Extraction = 'QA_Extraction'

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.get("http://www.python.org")
assert "Python" in driver.title

base_dir = os.path.dirname(__file__)
USERNAME = os.environ.get('AI_ACCOUNT')
PASSWORD = os.environ.get('AI_PASSWORD')
downloadFolder = str(Path.home() / 'Downloads')

def pushToGSheet():

    column_progress = []

    print('Updating Progress to GSheet...')
    #Google Sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, scope)
    client = gspread.authorize(creds)
    for files in os.listdir(QA_Extraction):
        key = files.split('-')[-4].split('_')[0]
        sheet = client.open(QA_Files[key][0]).worksheet(work_sheet)
        df = pd.read_csv(os.path.join(base_dir, QA_Extraction, files))
        df.fillna('', inplace=True)
        sheet.clear()
        sheet.insert_rows(df.values.tolist())

        print(f'#####GSHEET UPLOADED FOR {key}#####')

def login_to_platform():
    #Accesing SaaS
    driver.get("https://www.telusinternational.ai/")
    time.sleep(5)

    #Insert Creds
    login_form_email = driver.find_element_by_name('username').send_keys(USERNAME)
    continue_btn = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(2)
    login_form_pw = driver.find_element_by_name('password').send_keys(PASSWORD)
    signin_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(3)

    for item in QA_Files.values():
        scrapeProject(item)
    time.sleep(3)
    print('All CSVs downloaded')
    driver.quit()
    #moving files to better to_location
    if not os.path.exists(QA_Extraction):
        os.makedirs(QA_Extraction)
    move_files(downloadFolder, QA_Extraction, type=QA_Extraction)
    pushToGSheet()
    remove_files(os.path.join(base_dir,QA_Extraction))
    print('All results are online now')
        

def scrapeProject(input_url):

    driver.get(input_url[1])
    time.sleep(3)
    while True:
        try:
            print(f'Downloading CSV for {input_url[0]}')
            complete_data_btn = driver.find_element_by_xpath('//*[@id="all"]').click()
            time.sleep(2)
            csv_btn = driver.find_element_by_class_name('dropdown-item').click()
            time.sleep(1)
            break
        except NoSuchElementException:
            print('Retrying to download CSV')
        

if __name__=="__main__":
    login_to_platform()