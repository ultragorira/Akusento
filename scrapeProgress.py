from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import os
import time
import pandas as pd
import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials

from selenium import webdriver
import chromedriver_autoinstaller

JSON_creds = 'Bot_Creds.json'
Gsheet_UK = '116_EN_UK_Accents'
Gsheet_US = 'Test_116_EN_US_Accents'
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
username = os.environ.get('AI_ACCOUNT')
password = os.environ.get('AI_PASSWORD')

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
        column_progress.append(Cell(row,5, value=''.join(y[0])))
        column_progress.append(Cell(row,6, value=''.join(y[1])))
        row += 1  
                
        
    sheet.update_cells(column_progress)
    print('#####DONE#####')

def getLiveData():
    locale = input('US or UK: ')
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, scope)
    client = gspread.authorize(creds)
    sheet = client.open(Gsheet_US).worksheet(work_sheet) if locale == 'US' else client.open(Gsheet_UK).worksheet(work_sheet)

    df = pd.DataFrame(sheet.get_all_records())
    slim_list = list(zip(df['Assigned to Ref ID'],df['Rec Task URL'],df['Questionnaire URL'], df['Progress Rec Task'], df['Progress Questionnaire'], df['Status']))
    accessWebPages(slim_list, locale)
    

def accessWebPages(URLs, locale):    
    #Accesing SaaS
    driver.get("https://www.telusinternational.ai/")
    time.sleep(5)

    #Insert Creds
    login_form_email = driver.find_element_by_name('username').send_keys(username)
    continue_btn = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(2)
    login_form_pw = driver.find_element_by_name('password').send_keys(password)
    signin_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(3)

    for url in URLs:
        scrapeProject(url)
    
    pushToGSheet(zip(list_recording_completion, list_questionnaire_completion), locale)
    driver.quit()

def scrapeProject(input_url):

    if input_url[0] > 0 and input_url[5] != 'Complete' and input_url[5] != 'Complete Only Rec':
        while True:
            try:
                driver.get(input_url[1])
                print('Opening project..' + input_url[1])
                time.sleep(5)
                list_recording_completion.append(driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div[1]/div[2]').text)
                break
            except NoSuchElementException:
                print('Reloading ' + input_url[1])
        while True:
            try:
                print('Downloading CSV for you pal..')
                complete_data_btn = driver.find_element_by_xpath('//*[@id="all"]').click()
                time.sleep(2)
                csv_btn = driver.find_element_by_class_name('dropdown-item').click()
                break
            except NoSuchElementException:
                print('Retrying to download CSV')
        while True:
            try:
                driver.get(input_url[2])
                print('Opening project..' + input_url[2])
                time.sleep(5)
                list_questionnaire_completion.append(driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div[1]/div[2]').text)
                break
            except NoSuchElementException:
                print('Reloading ' + input_url[2])
    elif input_url[0] > 0:
        if input_url[3] == '100%':
            list_recording_completion.append('100%')
        else:
            list_recording_completion.append(str(input_url[3]))
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
 
    return(zip(list_recording_completion, list_questionnaire_completion))



# Run the file standalone.
if __name__=="__main__":
    getLiveData()