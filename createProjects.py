from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import *
import os
import time
import xlsxwriter



from selenium import webdriver
import chromedriver_autoinstaller


chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.get("http://www.python.org")
assert "Python" in driver.title

base_dir = os.path.dirname(__file__)
#driver = webdriver.Chrome(os.path.join(base_dir,'utils','chromedriver.exe'))
workingFolder = base_dir + r'\files'
list_titles = []
list_urls = []
guidelines_desc = 'Read the task provided to you by email. For each item, there will be instructions between []. Do not record those instructions, they are there just to guide you through the task.' 
USERNAME = os.environ.get('AI_ACCOUNT')
PASSWORD = os.environ.get('AI_PASSWORD')

def writeExcel(completeList):

    workbook = xlsxwriter.Workbook(os.path.join(base_dir,'ProjectsCreatedGengo.xlsx'))
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, "Project Name")
    worksheet.write(0, 1, "URL")

    row = 1

    for item in completeList:
        worksheet.write(row,0, item[0])
        worksheet.write(row,1, str(item[1] + '/progress'))

        row += 1


    workbook.close()

def hackSaas():

    print('Hacking SaaS...')
    accessWebPages()

def addMoreprojects(newCSV, isFirstProj):

    #New project view
    time.sleep(3)
    if (isFirstProj):
        #project_type = driver.find_element_by_xpath('//*[@id="root"]/div[2]/div/main/form/div/div[2]/div/div/div/div[1]/div/div[2]/div[1]/div/div/div[2]/div/svg').click()
        project_type = driver.find_element_by_xpath('//*[@id="react-select-2-input"]').send_keys('Audio Recording')
        project_type = driver.find_element_by_xpath('//*[@id="react-select-2-input"]').send_keys(Keys.ENTER)
        time.sleep(1)
        new_proj_title_txtbox = driver.find_element_by_xpath('//*[@id="projectName"]').send_keys(str('[116 - Accents] ' + newCSV.split('\\')[-1].replace('_',' ').replace('.csv','')))
        new_proj_title_txtbox = driver.find_element_by_xpath('//*[@id="projectDescription"]').send_keys(Keys.CONTROL + 'a')
        new_proj_title_txtbox = driver.find_element_by_xpath('//*[@id="projectDescription"]').send_keys(Keys.DELETE)
        new_proj_desc_txtbox = driver.find_element_by_xpath('//*[@id="projectDescription"]').send_keys(str(newCSV.split('\\')[-1].replace('_',' ').replace('.csv','') + ' - Please record the audio based on the guidelines provided to you via email.'))
        new_proj_language = driver.find_element_by_xpath('//*[@id="react-select-3-input"]').send_keys('English (United States)')
        new_proj_language = driver.find_element_by_xpath('//*[@id="react-select-3-input"]').send_keys(Keys.ENTER)
        time.sleep(4)

        save_submit_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/form/div/div[1]/div[1]/div/div/div[2]/button[2]').click() 
    else:
        while True:
            try:
                new_proj_title_txtbox = driver.find_element_by_xpath('//*[@id="projectName"]').send_keys(Keys.CONTROL + 'a')
                new_proj_title_txtbox = driver.find_element_by_xpath('//*[@id="projectName"]').send_keys(Keys.DELETE)
                new_proj_title_txtbox = driver.find_element_by_xpath('//*[@id="projectName"]').send_keys(str('[116 - Accents] ' + newCSV.split('\\')[-1].replace('_',' ').replace('.csv','')))
                break
            except NoSuchElementException:
                print('Did not find project title...')
                time.sleep(2)
        while True:
            try:
                new_proj_desc_txtbox = driver.find_element_by_xpath('//*[@id="projectDescription"]').send_keys(Keys.CONTROL + 'a')
                new_proj_desc_txtbox = driver.find_element_by_xpath('//*[@id="projectDescription"]').send_keys(Keys.DELETE)
                new_proj_desc_txtbox = driver.find_element_by_xpath('//*[@id="projectDescription"]').send_keys(str(newCSV.split('\\')[-1].replace('_',' ').replace('.csv','') + ' - Please record the audio based on the guidelines provided to you via email.'))
                break
            except NoSuchElementException:
                print('Did not find project Description...')
                time.sleep(2)
        
        time.sleep(2)
        while True:
            try:
                save_submit_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/form/div/div[1]/div[1]/div/div/div[2]/button[2]').click() 
            except NoSuchElementException:
                print('Could not find the save submit btn')
                time.sleep(1)

    #Appending titles to populate Excel with dump of projects
    list_titles.append(str('[116 - Accents] ' + newCSV.split('\\')[-1].replace('_',' ').replace('.csv','')))    
    time.sleep(2)
    while True:
        try:
            project_guidelines_txtbox = driver.find_element_by_xpath('//*[@id="projectInstructions"]').send_keys(guidelines_desc)
            break
        except NoSuchElementException:
            print('Did not find guidelines box...')
            time.sleep(2)
    #Uploading CSV
    time.sleep(2) 
    list_urls.append(driver.current_url)
    while True:
        try:
            choose_file_bt = driver.find_element_by_class_name('form-control-file').send_keys(newCSV)
            break
        except NoSuchElementException:
            print('Did not find Choose button..')
            time.sleep(2)

    time.sleep(2)

    while True:
        try:
            upload_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[2]/div/div/div[3]/div[2]/div[2]/div[2]/button').click()
            break
        except ElementClickInterceptedException:
            print('Upload btn not found for some reason') 
    
    time.sleep(2)
    while True:
        try:
            start_proj_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[1]/div[1]/div/div/div[2]/button').click()  
            time.sleep(2)
        except NoSuchElementException:
            print('Cannot find start proj button')
    while True:
        try:
            open_settings = driver.find_element_by_xpath('//*[@id="dropdown-action"]').click()
            time.sleep(1)
            clone_btn = driver.find_element_by_xpath('//*[@id="root"]/div[1]/main/div/div[1]/div[1]/div/div/div[2]/div/div/a[1]').click()
        except NoSuchElementException:
            print('Issues when cloning')
            
def accessWebPages():    
    #Accesing SaaS
    driver.get("https://www.telusinternational.ai/")
    time.sleep(5)

    isFirstProj = True

#Insert Creds
    login_form_email = driver.find_element_by_name('username').send_keys(USERNAME)
    continue_btn = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(2)
    login_form_pw = driver.find_element_by_name("password").send_keys(PASSWORD)
    signin_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(3)

    #Create projects in bulk one after the other
    
    for root, dirs, files in os.walk(workingFolder):
        for file in files:
            time.sleep(2)
            if (isFirstProj):
                #MainView Opening New Project
                #driver.find_element_by_xpath('//button[contains(text(), "New Project")]').click() 
                driver.get('https://www.telusinternational.ai/home/projects/create')
                addMoreprojects(os.path.join(root,file), isFirstProj)
                isFirstProj = False
            else:
                addMoreprojects(os.path.join(root,file), isFirstProj)

    time.sleep(2)
    back_to_main = driver.find_element_by_xpath('//*[@id="root"]/header/div[1]/a').click()
    print('All projects created rorisuderuka!')
    writeExcel(zip(list_titles, list_urls))
    driver.quit()
    


# Run as standalone.
if __name__=="__main__":
    hackSaas()