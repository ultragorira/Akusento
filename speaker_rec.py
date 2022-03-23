#Speaker Recognition from https://github.com/speechbrain/speechbrain
from speechbrain.pretrained import SpeakerRecognition
import os
import torch
import csv

verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")
HEADERS = ['Filename', 'Score', 'Prediction']

def verify_speaker_authenticity(folder_location):

    package_name = folder_location.split('\\')[-1].split('_')[0]
    print(f'Checking package {package_name}')

    different_voice_files = []
    for root, dirs, files in os.walk(folder_location):
        for file in files[1:]:
            #Comparing first files vs rest of audios
            score, prediction = verification.verify_files(os.path.join(root,files[0]),os.path.join(root, file))
            #print(score)
            #print(prediction)
            #This means voice in file x is different than file 1
            if prediction.tolist()[0] == False:
                different_voice_files.append([file, score.tolist()[0], prediction.tolist()[0]])
                print(f'File {file} is a different voice')

    if len(different_voice_files) > 0:
        print(f'Package {package_name} has some issues, writing report.')
        write_report(different_voice_files)
    else:
        print(f'Package {package_name} is fine')

def write_report(different_voice_files):

    package_name = different_voice_files[0][0].split('_')[0]

    with open(package_name+'.csv', mode='w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(HEADERS)
        csv_writer.writerows(different_voice_files)
    print(f'Report created for {package_name}')

folder = r'\\tre-s-file01\Customers\Amazon\116_Lab126_Accented_speakers_collection_US_UK\Production\01_Audio\02_Uploaded_ToAPConverted1616\US\025L'
if __name__ =="__main__":
    verify_speaker_authenticity(folder)