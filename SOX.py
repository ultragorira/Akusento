# Author: Loris De Luca
# Prerequisite: pip install pathlib

import os
import subprocess
import pathlib

workingFolder = os.path.dirname(__file__)
#This path is in system env variables
soxLocation = os.environ.get('SOX_LOCATION')

#####################################################################################
#SOX convertion
def runSOX():
     
    path = input('Add the path: ')
     
    for root, dirs, files in os.walk(path):
        rootMain = pathlib.PurePath(root).parts[-1:] 
        rootMaintoString = str(rootMain[0])
        outputFolder = workingFolder + r'\FilesSoxed\\' + rootMaintoString
        for filename in files:
            if not os.path.exists(outputFolder):
                os.makedirs(outputFolder)
            outputFile = outputFolder + '\\' +filename
            subprocess.call([soxLocation, os.path.join(root, filename), '-r', '16k','-t', 'wavpcm', '-b', '16', outputFile],shell = True)   
    print('***Sox processing completed***')
    os.startfile(outputFolder)

# Run as standalone.

if __name__=="__main__":
    runSOX()