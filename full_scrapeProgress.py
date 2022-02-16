from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import os
import time
from datetime import datetime
import pandas as pd
import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
from functions import move_files
from scheduled_multithreadDownload import call_multiple_threads
from SOX import runSOX
from paths import targetFolder, Sox_targetFolder,Audio_targetFolder
from pathlib import Path
from selenium import webdriver
import chromedriver_autoinstaller

JSON_creds = 'Bot_Creds.json'
Gsheet_UK = 'Tech_116_EN_UK_Accents'
Gsheet_US = 'Tech_116_EN_US_Accents'
work_sheet = 'Projects_Allocation'

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.get("http://www.python.org")
assert "Python" in driver.title

base_dir = os.path.dirname(__file__)
list_recording_completion = []
list_questionnaire_completion = []
dates = []
USERNAME = os.environ.get('AI_ACCOUNT')
PASSWORD = os.environ.get('AI_PASSWORD')

downloadFolder = str(Path.home() / 'Downloads')

def pushToGSheet(progress_list, locale):

    column_progress = []

    print('Updating Progress to GSheet...')
    #Google Sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, scope)
    client = gspread.authorize(creds)
    sheet = client.open(Gsheet_US).worksheet(work_sheet) if locale == 'US' else client.open(Gsheet_UK).worksheet(work_sheet)

    row = 2

    for y in progress_list:
        column_progress.append(Cell(row,6, value=''.join(y[0])))
        column_progress.append(Cell(row,7, value=''.join(y[1])))
        column_progress.append(Cell(row,12, value=''.join(y[2])))
        row += 1  
                
        
    sheet.update_cells(column_progress)
    print('#####GSHEET UPLOADED#####')

    list_recording_completion.clear()
    list_questionnaire_completion.clear()
    dates.clear()

def getLiveData():
    locale = ['US', 'UK']
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, scope)
    client = gspread.authorize(creds)
    login_to_platform()
    for loc in locale:
        print(f'Checking now {loc}')
        sheet = client.open(Gsheet_US).worksheet(work_sheet) if loc == 'US' else client.open(Gsheet_UK).worksheet(work_sheet)
        df = pd.DataFrame(sheet.get_all_records())
        slim_list = list(zip(df['Assigned to Ref ID'],df['Rec Task URL'],df['Questionnaire URL'], df['Progress Rec Task'], df['Progress Questionnaire'], df['Status'], df['Date Download'], df['Soxed'], df['S3']))
        accessWebPages(slim_list, loc)
    driver.quit()
    #Moving CSVs to Server
    csv_audio_to_download = move_files(downloadFolder, targetFolder)
    #Download Audios
    call_multiple_threads(csv_audio_to_download)
    #SOX all files
    print('Soxing Files')
    runSOX('./Downloaded')
    #Move SOXed files to Server
    move_files('.FilesSoxed', Sox_targetFolder, type='Upload_Sox')
    print('Soxed files pushed to server')
    #Move Originals to Server
    move_files('Downloaded', Audio_targetFolder, type='Upload_Original')
    print('Original files pushed to server')
    #Upload audios to S3

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

    

def accessWebPages(URLs, locale):    

    for url in URLs:
        scrapeProject(url)
    
    pushToGSheet(zip(list_recording_completion, list_questionnaire_completion, dates), locale)
    #driver.quit()

def scrapeProject(input_url):

    if input_url[0] !='' and input_url[5] != 'Complete' and input_url[5] != 'Complete Only Rec':
        while True:
            try:
                driver.get(input_url[1])
                print('Opening project..' + input_url[1])
                time.sleep(5)
                list_recording_completion.append(driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div[1]/div[2]').text)
                current_status = list_recording_completion[-1]
                break
            except NoSuchElementException:
                print('Reloading ' + input_url[1])
        if current_status == '100%':
            while True:
                try:
                    print('Downloading CSV for you pal..')
                    complete_data_btn = driver.find_element_by_xpath('//*[@id="all"]').click()
                    time.sleep(2)
                    csv_btn = driver.find_element_by_class_name('dropdown-item').click()
                    dates.append(str(datetime.today()).split()[0])
                    break
                except NoSuchElementException:
                    print('Retrying to download CSV')
        else:
            dates.append(str(input_url[6]))
        while True:
            try:
                driver.get(input_url[2])
                print('Opening project..' + input_url[2])
                time.sleep(5)
                list_questionnaire_completion.append(driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div[1]/div[2]').text)
                break
            except NoSuchElementException:
                print('Reloading ' + input_url[2])
    elif input_url[0] != '':
        if input_url[3] == '100%':
            list_recording_completion.append('100%')
        else:
            list_recording_completion.append(str(input_url[3]))
        dates.append(str(input_url[6]))
        if input_url[5] == 'Complete Only Rec':
            while True:
                try:
                    driver.get(input_url[2])
                    print('Opening project..' + input_url[2])
                    time.sleep(5)
                    list_questionnaire_completion.append(driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div[1]/div[2]').text)
                    break
                except NoSuchElementException:
                    print('Reloading ' + input_url[2])
        else:
            list_questionnaire_completion.append(str(input_url[4]))
    else:
        list_recording_completion.append('0%')
        list_questionnaire_completion.append('0%')
        dates.append(str(input_url[6]))
 
    return(zip(list_recording_completion, list_questionnaire_completion, dates))



# Run the file standalone.
if __name__=="__main__":
    getLiveData()