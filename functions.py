# Author: Loris De Luca
# Common functions

import os
import glob
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from shutil import move
import time, shutil

workingFolder = os.path.dirname(__file__)
#Change below depending on where is your SOX
soxLocation = os.environ.get('SOX_LOCATION')     

def calculateSNR(path, segment_lenght):
    
    if (path.endswith('.wav')):
        cmd = subprocess.Popen([soxLocation, path, '-n', 'stats','-w', str(segment_lenght)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stderrdata, stdoutdata = cmd.communicate()
        SNR = round(float(stdoutdata.decode('utf-8').split('\r\n')[5].split(' ')[-1])-float(stdoutdata.decode('utf-8').split('\r\n')[6].split(' ')[-1]))
        #print ('File {file} has {snr} value for SNR'.format(file=filename, snr=SNR))
        return(str(SNR))
    

def generate_UUID(userID, collectionID, language):

    return(str(uuid.uuid5(uuid.NAMESPACE_DNS, userID + '_' + collectionID + '_' + language)))


def calcEpoch(timeFromMediaInfo):
    #Conversion of time to Epoch standards
    datetime_object = datetime.strptime(timeFromMediaInfo.replace('UTC ',''), '%Y-%m-%d %H:%M:%S.%f')
    epochTime = int(round(datetime.timestamp(datetime_object)* 1000))
    return(str(epochTime))


def move_files(from_location, to_location, type='Download'):
    
    files_to_download = []
    today = str(datetime.today()).split()[0]
    if type=='Download':
        for files in os.listdir(from_location):
            if files.endswith('.csv') and 'Accents' in files:
                time_format = time.gmtime(os.path.getmtime(os.path.join(from_location,files)))
                destination_folder = os.path.join(to_location, files.split('-')[4][2:])
                if str(time_format.tm_year)+'-'+str(time_format.tm_mon).zfill(2)+'-'+str(time_format.tm_mday) == today:
                    shutil.move(os.path.join(from_location,files), destination_folder)
                    #Saving the list of files to then launch multithread download
                    files_to_download.append(os.path.join(destination_folder, files))
                    output = '/'.join(destination_folder.split('\\')[6:9])
                    print(f'Moved file {files} to {output}')
    elif type=='Upload_Sox':
        for files in os.listdir(from_location):
            shutil.move(os.path.join(from_location,files), to_location)
    elif type=='Upload_Original':
        for files in os.listdir(from_location):
            if int(files[:3]) <= 56:
                shutil.move(os.path.join(from_location,files), os.path.join(to_location,'US', '_Move_here_after_SOX'))
            else:
                shutil.move(os.path.join(from_location,files), os.path.join(to_location,'UK', '_Move_here_after_SOX'))
    elif type=='QA_Extraction':
        for files in os.listdir(from_location):
            if files.endswith('.csv') and 'Accents-QA' in files:
                time_format = time.gmtime(os.path.getmtime(os.path.join(from_location,files)))
                if str(time_format.tm_year)+'-'+str(time_format.tm_mon).zfill(2)+'-'+str(time_format.tm_mday) == today:
                    shutil.move(os.path.join(from_location,files), to_location)    
    if type=='Download':
        return (files_to_download)

def remove_files(location):
    for files in os.listdir(location):
        os.unlink(os.path.join(location, files))