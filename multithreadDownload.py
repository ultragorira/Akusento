# Author: Loris De Luca
# Prerequisite: pip install , selenium. Chromedriver.exe available in utils
# Script to download audios for projects in the Arabic collection

from selenium import webdriver
from selenium.common.exceptions import *
import pandas as pd
import time
import os
from pathlib import Path
import shutil, subprocess, threading


workingFolder = os.path.dirname(__file__)
downloadFolder = str(Path.home() / 'Downloads')
ffmpegLoc = 'utils/ffmpeg.exe'
USERNAME = 'lb.apollo.project@gmail.com'
PASSWORD = 'Admin001!!'
urls = []
keys = [] 
ids = []


def hackSaas():

    gengo_report = input('Give path to the Gengo Report: ')
    df = pd.read_csv(gengo_report, usecols=['id', 'key', 'status', 'output1'])
    #taking only the DONE files 
    df = df[(df['status'] =='done')] 
    urls = df['output1'].tolist()
    keys = df['key'].tolist()
    ids = df['id'].tolist()


    #print('Hacking SaaS...')
    accessWebPages(USERNAME, PASSWORD,ids, keys, urls)

    

def accessWebPages(login_mail, login_pw, ids, keys, URLs):  

    options = webdriver.ChromeOptions()
    #disabling terminal msg where selenium instance is listening
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(os.path.join(workingFolder,'utils','chromedriver.exe'), options=options)

    page_LoadedCorrectly = True
    #Accesing SaaS
    driver.get("https://ai.lionbridge.com/")
    time.sleep(5)

    #Insert Creds
    login_form_email = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/div/input').send_keys(login_mail)
    continue_btn = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(2)
    login_form_pw = driver.find_element_by_name("password").send_keys(login_pw)
    signin_bt = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/form/button').click()
    time.sleep(3)
    

    for url in URLs:
        driver.get(url.split(';')[0])
        while True:
            try:
                time.sleep(2)
                #Checking if correct page loaded
                page_loaded = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div/div/main/div/div/a')
                break
            except NoSuchElementException:
                print('Page ' + url.split(';')[0] + ' did not load, reloading...')
                driver.get(url.split(';')[0])
                time.sleep(2)

    rename(ids, keys, URLs)
    time.sleep(3)
    driver.quit()

def rename(list_i, list_o, urls):

    file_suffix = ''

    if ('webm' in urls[0].split(';')[1]):
        file_suffix = '_output_1.webm'
    else:
        file_suffix = '_output_1.wav'

    time.sleep(20)
    index = 0
    for i in list_i:
        project_ID = str('project_'+((urls[index].split(';')[0]).split('/')[5])+'_item_')
        if not os.path.exists(str(workingFolder + '\\Downloaded\\' + list_o[index][0:4])):
                os.makedirs(str(workingFolder + '\\Downloaded\\' + list_o[index][0:4]))
        shutil.move(str(downloadFolder + '\\' +project_ID + i + file_suffix), str(workingFolder + '\\Downloaded\\' + list_o[index][0:4] + '\\' + list_o[index] + '.' + file_suffix.split('.')[1]))
        index += 1 

    #if webm convert to wav
    #check if webm or wav output
    if ('webm' in urls[0].split(';')[1]):
        convertWebmToWav(list_o[0][0:4])
        deleteWebm(list_o[0][0:4])
    #else:
    #    driver.quit()
    print(f'####### Files downloaded for {list_o[0][0:4]}')
    os.startfile(os.path.join(workingFolder,'Downloaded'))

def convertWebmToWav(participant_folder):

    ffmpeg = os.path.join(workingFolder,ffmpegLoc)
    for root, dirs, files in os.walk(os.path.join(workingFolder,'Downloaded',participant_folder)):
        for filename in files:
                outputFile = os.path.join(workingFolder,'Downloaded',participant_folder) + '\\' +filename
                subprocess.call([ffmpeg, '-i', os.path.join(root, filename), '-c:a', 'pcm_s32le', outputFile.replace('.webm', '.wav')],shell = True)


def deleteWebm(participant_folder):

    outputFolder = os.path.join(workingFolder,'Downloaded',participant_folder)
    for root, dirs, files in os.walk(outputFolder):
        for filename in files:        
            file_path = os.path.join(root, filename)
            try:
                if ('.webm' in filename):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    #print('############Files Downloaded and converted#################')
    #driver.quit()
    os.startfile(os.path.join(workingFolder,'Downloaded'))

def runThreads():

    numberThreads = input('How many threads you want to run: ')
    threads = []

    for i in range(int(numberThreads)):
        t = threading.Thread(target=hackSaas)
        t.daemon = True
        threads.append(t)

    for i in range(int(numberThreads)):
        threads[i].start()
    
    for i in range(int(numberThreads)):
        threads[i].join()

# Run as standalone.
if __name__=="__main__":
    runThreads()