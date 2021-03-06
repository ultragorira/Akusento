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
    data['sessionLocalStartTime'] = int(full_data['sessionLocalStartTime'][rownum]) 
    data['audioFileName'] = full_data['audioFileName'][rownum]
    data['collectionId'] = full_data['collectionId'][rownum]
    data['collectionUuid'] = full_data['collectionUuid'][rownum] 
    data['audioFormat'] = {}
    if (full_data['bigEndian'][rownum] == 'Little'):
      endian = "true"
    else:
      endian = "false" 
    data['audioFormat']['bigEndian'] = endian
    data['audioFormat']['channels'] = int(full_data['channels'][rownum])
    data['audioFormat']['encoding'] = full_data['encoding'][rownum]
    data['audioFormat']['frameRate'] = int(full_data['frameRate'][rownum])
    data['audioFormat']['frameSize'] = int(full_data['frameSize'][rownum])
    data['audioFormat']['sampleRate'] = int(full_data['sampleRate'][rownum])
    data['audioFormat']['sampleSizeInBits'] = int(full_data['sampleSizeInBits'][rownum])
    data['audioFormat']['audioDurationMillis'] = int(full_data['audioDurationMillis'][rownum])
    data['audioFormat']['format'] = full_data['format'][rownum]
    data['audioFormat']['sourceType'] = full_data['sourceType'][rownum]
    data['sessionInfo'] = {}
    data['sessionInfo']['languageCollected'] = full_data['languageCollected'][rownum]
    data['sessionInfo']['ageRange'] = full_data['ageRange'][rownum]
    data['sessionInfo']['gender'] = full_data['gender'][rownum]
    data['sessionInfo']['countryLived'] = full_data['countryLived'][rownum]
    data['sessionInfo']['languageSpokenDaily'] = full_data['languageSpokenDaily'][rownum]
    data['sessionInfo']['primaryMicrophone'] = full_data['primaryMicrophone'][rownum]
    data['transcription'] = {}
    data['transcription']['domain'] = full_data['domain'][rownum] if full_data['domain'][rownum] != '' else 'null'
    data['transcription']['id'] = str(full_data['id'][rownum]).zfill(2)
    data['transcription']['phrase'] = full_data['phrase'][rownum]
    data['transcription']['annotation'] = full_data['annotation'][rownum]
    data['transcription']['startEndpoint'] = full_data['startEndpoint'][rownum]
    data['transcription']['stopEndpoint'] = full_data['stopEndpoint'][rownum]
    data['transcription']['type'] = full_data['type'][rownum]
    data['transcription']['qualityChecks'] = {}
    data['transcription']['wakeword'] = full_data['wakeword'][rownum]
    data['transcription']['intent'] = full_data['intent'][rownum] if full_data['intent'][rownum] != '' else 'null'
    data['additionalMetadata'] = {}
    data['additionalMetadata']['phoneModel'] = full_data['phoneModel'][rownum]
    data['additionalMetadata']['phoneBrand'] = full_data['phoneBrand'][rownum]
    data['additionalMetadata']['speakerId'] = full_data['speakerId'][rownum]
    data['additionalMetadata']['backgroundNoiseLevelInDb'] = str(full_data['backgroundNoiseLevelInDb'][rownum])
    data['additionalMetadata']['distance'] = full_data['distance'][rownum]
    data['additionalMetadata']['backgroundCondition'] = full_data['backgroundCondition'][rownum]
    data['additionalMetadata']['operatingSystem'] = full_data['operatingSystem'][rownum]
    data['additionalMetadata']['backgroundNoise'] = full_data['backgroundNoise'][rownum]
    data['additionalMetadata']['speechType'] = str(full_data['speechType'][rownum]).rstrip()
    data['additionalMetadata']['accentLevel'] = full_data['accentLevel'][rownum]
    data['additionalMetadata']['surveyQuestion1'] = str(full_data['surveyQuestion1'][rownum])
    data['additionalMetadata']['surveyQuestion2'] = str(full_data['surveyQuestion2'][rownum])
    data['additionalMetadata']['surveyQuestion3'] = str(full_data['surveyQuestion3'][rownum])
    data['additionalMetadata']['surveyQuestion4'] = str(full_data['surveyQuestion4'][rownum])
    data['additionalMetadata']['surveyQuestion4a'] = str(full_data['surveyQuestion4a'][rownum])
    data['additionalMetadata']['surveyQuestion5'] = str(full_data['surveyQuestion5'][rownum])

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
  create_JSONS(df_by_id.reset_index())

if __name__ == '__main__':
  read_data_from_gspread()