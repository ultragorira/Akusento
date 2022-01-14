import os
import json
import pandas as pd
import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials

base_dir = os.path.dirname(__file__)
JSON_Folder = os.path.join(base_dir, 'JSON_Output/')

if not os.path.exists(JSON_Folder):
  os.makedirs(JSON_Folder)

def create_JSONS(full_data):
  # List to hold dictionaries
  json_list = []
  fileCount = 0

  # Iterate through each row in worksheet and fetch values into dict
  for rownum in range(len(full_data.index)):
    data = {}
    data['sessionLocalStartTime'] = int(full_data['sessionLocalStartTime'][rownum+1]) 
    data['audioFileName'] = full_data['audioFileName'][rownum+1]
    data['collectionId'] = full_data['collectionId'][rownum+1]
    data['collectionUuid'] = full_data['collectionUuid'][rownum+1] 
    data['audioFormat'] = {}
    if (full_data['bigEndian'][rownum+1] == 'Little'):
      endian = "true"
    else:
      endian = "false" 
    data['audioFormat']['bigEndian'] = endian
    data['audioFormat']['channels'] = int(full_data['channels'][rownum+1])
    data['audioFormat']['encoding'] = full_data['encoding'][rownum+1]
    data['audioFormat']['frameRate'] = int(full_data['frameRate'][rownum+1])
    data['audioFormat']['frameSize'] = int(full_data['frameSize'][rownum+1])
    data['audioFormat']['sampleRate'] = int(full_data['sampleRate'][rownum+1])
    data['audioFormat']['sampleSizeInBits'] = int(full_data['sampleSizeInBits'][rownum+1])
    data['audioFormat']['audioDurationMillis'] = int(full_data['audioDurationMillis'][rownum+1])
    data['audioFormat']['format'] = full_data['format'][rownum+1]
    data['audioFormat']['sourceType'] = full_data['sourceType'][rownum+1]
    data['sessionInfo'] = {}
    data['sessionInfo']['languageCollected'] = full_data['languageCollected'][rownum+1]
    data['sessionInfo']['ageRange'] = full_data['ageRange'][rownum+1]
    data['sessionInfo']['gender'] = full_data['gender'][rownum+1]
    data['sessionInfo']['countryLived'] = full_data['countryLived'][rownum+1]
    data['sessionInfo']['languageSpokenDaily'] = full_data['languageSpokenDaily'][rownum+1]
    data['sessionInfo']['primaryMicrophone'] = full_data['primaryMicrophone'][rownum+1]
    data['transcription'] = {}
    data['transcription']['domain'] = full_data['domain'][rownum+1]
    data['transcription']['id'] = str(full_data['id'][rownum+1])
    data['transcription']['phrase'] = full_data['phrase'][rownum+1]
    data['transcription']['annotation'] = full_data['annotation'][rownum+1]
    data['transcription']['startEndpoint'] = full_data['startEndpoint'][rownum+1]
    data['transcription']['stopEndpoint'] = full_data['stopEndpoint'][rownum+1]
    data['transcription']['type'] = full_data['type'][rownum+1]
    data['transcription']['qualityChecks'] = {}
    data['transcription']['wakeword'] = full_data['wakeword'][rownum+1]
    data['transcription']['intent'] = full_data['intent'][rownum+1]
    data['additionalMetadata'] = {}
    data['additionalMetadata']['phoneModel'] = full_data['phoneModel'][rownum+1]
    data['additionalMetadata']['phoneBrand'] = full_data['phoneBrand'][rownum+1]
    data['additionalMetadata']['speakerId'] = full_data['speakerId'][rownum+1]
    data['additionalMetadata']['backgroundNoiseLevelInDb'] = str(full_data['backgroundNoiseLevelInDb'][rownum+1])
    data['additionalMetadata']['distance'] = full_data['distance'][rownum+1]
    data['additionalMetadata']['backgroundCondition'] = full_data['backgroundCondition'][rownum+1]
    data['additionalMetadata']['operatingSystem'] = full_data['operatingSystem'][rownum+1]
    data['additionalMetadata']['speechType'] = str(full_data['speechType'][rownum+1]).rstrip()
    data['additionalMetadata']['accentLevel'] = full_data['accentLevel'][rownum+1]
    data['additionalMetadata']['surveyQuestion1'] = full_data['surveyQuestion1'][rownum+1]
    data['additionalMetadata']['surveyQuestion2'] = full_data['surveyQuestion2'][rownum+1]
    data['additionalMetadata']['surveyQuestion3'] = full_data['surveyQuestion3'][rownum+1]
    data['additionalMetadata']['surveyQuestion4'] = full_data['surveyQuestion4'][rownum+1]
    data['additionalMetadata']['surveyQuestion4a'] = full_data['surveyQuestion4a'][rownum+1]
    data['additionalMetadata']['surveyQuestion5'] = full_data['surveyQuestion5'][rownum+1]

    if data['sessionLocalStartTime'] == "None" or data['sessionLocalStartTime'] == "" or data['sessionLocalStartTime'] == None:
      break
    j = json.dumps(data, indent=4, ensure_ascii=False).encode('utf8')
    # Write to file
    with open(os.path.join(JSON_Folder, data['audioFileName'].replace('wav','') + 'json'), 'wb') as f:
      f.write(j)
      json_list.clear()
    fileCount += 1
  print("{} JSON files have been generated!".format(fileCount))
  os.startfile(JSON_Folder)


def read_data_from_gspread():

  id_participant = input('Give the ID of participants, remember to include L at the end: ')
  #Google Sheet
  scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name("Bot_Creds.json", scope)
  client = gspread.authorize(creds)
  sheet = client.open('TECH_ACCENTS').worksheet('JSON_DumpCollection')  # Open the spreadhseet

  print('Getting Data from Gsheet ' + sheet.title) 
  df = pd.DataFrame(sheet.get_all_records())
  #Filtering the dataframe by only the ID interested in
  df_by_id = df.loc[df['audioFileName'].str.contains(str(id_participant), case=False)]
  create_JSONS(df_by_id)

if __name__ == '__main__':
  read_data_from_gspread()