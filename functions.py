# Author: Loris De Luca
# Common functions

import os
import glob
import subprocess
import uuid
from datetime import datetime

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
