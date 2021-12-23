#Author: Loris De Luca
import os
from pymediainfo import MediaInfo
import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
import functions as general_functions
import pandas as pd


def pushToGSheet(location, questionnaire):
    #Google Sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("Bot_Creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open('TECH_ACCENTS').worksheet('JSON_Raw_Py')  # Open the spreadhseet
    collectionID = 'FI-en-US-Vendor'

    list_questionnaire = pd.read_csv(questionnaire)
    responses = list(zip(list_questionnaire['output1'],list_questionnaire['output2'], list_questionnaire['output3'], list_questionnaire['output4'], list_questionnaire['output5'], list_questionnaire['output6']))
    #print(responses)
    files = [f for f in os.listdir(location) if os.path.isfile(os.path.join(location,f))]

    row = 2
    column1 = []
    column2 = []
    column3 = []
    column4 = []
    column5 = []
    column6 = []
    column7 = []
    column8 = []
    column9 = []
    column10 = []
    column11 = []
    column12 = []
    column13 = []
    column14 = []
    column15 = []
    column16 = []
    column17 = []
    column18 = []
    column19 = []
    column20 = []
    column21 = []
    column22 = []
    column23 = []

    for audio in files:
        media_info = MediaInfo.parse(os.path.join(location,audio))
        for track in media_info.tracks:
            if track.track_type == 'Audio':
                column1.append(Cell(row,1, value=''.join(general_functions.calcEpoch(media_info.tracks[0].file_last_modification_date))))
                column2.append(Cell(row,2, value=''.join(audio)))
                column3.append(Cell(row,3, value=''.join(str(collectionID))))
                column4.append(Cell(row,4, value=''.join(general_functions.generate_UUID(audio[0:4], collectionID, audio.split('_')[-1]))))
                column5.append(Cell(row,5, value=''.join(track.format_settings__endianness)))
                column6.append(Cell(row,6, value=''.join(str(track.channel_s))))
                column7.append(Cell(row,7, value=''.join(track.commercial_name+'_'+track.format_settings__sign.upper())))
                column8.append(Cell(row,8, value=''.join(str(track.sampling_rate))))
                column9.append(Cell(row,9, value=''.join(str(track.bit_depth))))
                column10.append(Cell(row,10, value=''.join(str(track.sampling_rate))))
                column11.append(Cell(row,11, value=''.join(str(track.bit_depth))))
                column12.append(Cell(row,12, value=''.join(str(track.duration))))
                column13.append(Cell(row,13, value=''.join(str.upper(media_info.tracks[0].file_extension))))
                column14.append(Cell(row,14,value=''.join('Mobile')))
                column15.append(Cell(row,15, value=''.join('en-US')))
                column16.append(Cell(row,19, value=''.join('en')))
                column17.append(Cell(row,20, value=''.join('Default Audio Device')))
                column18.append(Cell(row,43, value=''.join(responses[0][0])))
                column19.append(Cell(row,44, value=''.join(responses[0][1])))
                column20.append(Cell(row,45, value=''.join(responses[0][2])))
                column21.append(Cell(row,46, value=''.join(responses[0][3])))
                column22.append(Cell(row,47, value=''.join(responses[0][4])))
                column23.append(Cell(row,48, value=''.join(responses[0][5])))

            
                row += 1  
                
        
    sheet.update_cells(column1)
    sheet.update_cells(column2)
    sheet.update_cells(column3)
    sheet.update_cells(column4)
    sheet.update_cells(column5)
    sheet.update_cells(column6)
    sheet.update_cells(column7)
    sheet.update_cells(column8)
    sheet.update_cells(column9)
    sheet.update_cells(column10)
    sheet.update_cells(column11)
    sheet.update_cells(column12)
    sheet.update_cells(column12)
    sheet.update_cells(column13)
    sheet.update_cells(column14)
    sheet.update_cells(column15)
    sheet.update_cells(column16)
    sheet.update_cells(column17)
    sheet.update_cells(column18)
    sheet.update_cells(column19)
    sheet.update_cells(column20)    
    sheet.update_cells(column21)
    sheet.update_cells(column22)
    sheet.update_cells(column23)

    print('### 終わった - Owatta! ###') 

def getMediaInfo():

    workingFolder = input('Provide Loc of audio files: ')
    questionnaire = input('Provide the questionnaire CSV: ')
    pushToGSheet(workingFolder, questionnaire)


# Run the file standalone.
if __name__=="__main__":
    getMediaInfo()