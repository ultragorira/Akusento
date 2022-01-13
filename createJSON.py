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
  for rownum in range(2, len(full_data)):
      data = {}
      data['sessionLocalStartTime'] = full_data.cell(rownum, 1).value  
      data['audioFileName'] = full_data.cell(rownum, 2).value 
      data['collectionId'] = full_data.cell(rownum, 3).value 
      data['collectionUuid'] = full_data.cell(rownum,4).value 
      data['audioFormat'] = {}
      if (full_data.cell(rownum, 5).value == 'Little'):
          endian = True
      else:
          endian = False 
      data['audioFormat']['bigEndian'] = endian
      data['audioFormat']['channels'] = full_data.cell(rownum, 6).value
      data['audioFormat']['encoding'] = full_data.cell(rownum, 7).value
      data['audioFormat']['frameRate'] = full_data.cell(rownum, 8).value
      data['audioFormat']['frameSize'] = full_data.cell(rownum, 9).value
      data['audioFormat']['sampleRate'] = full_data.cell(rownum, 10).value
      data['audioFormat']['sampleSizeInBits'] = full_data.cell(rownum, 11).value
      data['audioFormat']['audioDurationMillis'] = full_data.cell(rownum, 12).value
      data['audioFormat']['format'] = full_data.cell(rownum, 13).value
      data['audioFormat']['sourceType'] = full_data.cell(rownum, 14).value
      data['sessionInfo'] = {}
      data['sessionInfo']['languageCollected'] = full_data.cell(rownum, 15).value
      data['sessionInfo']['ageRange'] = full_data.cell(rownum, 16).value
      data['sessionInfo']['gender'] = full_data.cell(rownum, 17).value
      data['sessionInfo']['countryLived'] = full_data.cell(rownum, 18).value
      data['sessionInfo']['languageSpokenDaily'] = full_data.cell(rownum, 19).value
      data['sessionInfo']['primaryMicrophone'] = full_data.cell(rownum, 20).value
      data['transcription'] = {}
      data['transcription']['audioDurationMillis'] = full_data.cell(rownum, 21).value
      data['transcription']['domain'] = full_data.cell(rownum, 22).value
      data['transcription']['id'] = str(full_data.cell(rownum, 23).value)
      data['transcription']['phrase'] = full_data.cell(rownum, 24).value
      data['transcription']['startEndpoint'] = full_data.cell(rownum, 25).value
      data['transcription']['stopEndpoint'] = full_data.cell(rownum, 26).value
      data['transcription']['type'] = full_data.cell(rownum, 27).value
      data['transcription']['qualityChecks'] = {}
      data['transcription']['wakeword'] = full_data.cell(rownum, 29).value
      data['transcription']['intent'] = full_data.cell(rownum,30).value
      data['additionalMetadata'] = {}
      data['additionalMetadata']['annotation'] = {}
      data['additionalMetadata']['phoneModel'] = full_data.cell(rownum, 32).value
      data['additionalMetadata']['phoneBrand'] = full_data.cell(rownum, 33).value
      data['additionalMetadata']['speakerId'] = full_data.cell(rownum, 34).value
      data['additionalMetadata']['backgroundNoiseLevelInDb'] = str(full_data.cell(rownum, 35).value)
      data['additionalMetadata']['operatingSystem'] = full_data.cell(rownum, 36).value
      data['additionalMetadata']['backgroundNoise'] = full_data.cell(rownum, 37).value
      data['additionalMetadata']['speechImpediment'] = full_data.cell(rownum, 38).value
      data['additionalMetadata']['dialect'] = full_data.cell(rownum,39).value
      if (full_data.cell(rownum,40).value == 'Chicago'):
        region = 'Chicago'
      elif (full_data.cell(rownum,40).value == 'North East'):
        region = 'Northeast'
      elif ((full_data.cell(rownum,40).value).split('-')[0] == 'South'):
        region = 'South'
      else:
        region = 'Other'
      data['additionalMetadata']['region'] = full_data.cell(rownum,40).value
      data['additionalMetadata']['other_city_state'] = full_data.cell(rownum,41).value

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

  df = pd.DataFrame(sheet.get_all_records())
  #Filtering the dataframe by only the ID interested in
  df_by_id = df.loc[df['audioFileName'].str.contains(str(id_participant), case=False)]
  print(df_by_id)
  create_JSONS(df_by_id)

if __name__ == '__main__':
  read_data_from_gspread()