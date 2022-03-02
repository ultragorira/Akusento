import os.path
import io
from cv2 import merge
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from pathlib import Path

from pytest import skip

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
JSON_creds = 'Bot_Creds.json'
destinationFolder = "Downloaded"
headers= ['Payment Type','Payment Period ID','Email Address','First Name','Last Name',
'Tax Country','Payment Currency Code','Payment Amount','Workday Project ID',
'Workday Project Name','Pmt Method','Bank Name','Institution Number or Swift',
'Routing Transit Number','Bank Account Number','IBAN','Beneficiary Name',
'Address Line 1 for Wire','Address Line 2 for Wire','City for Wire','Province for Wire',
'Country for Wire','Wire Comment for Wire'
]

def main():
    folderId = input('Give folder ID: ')
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, SCOPES)
    service = build('drive', 'v3', credentials=creds)
    #folderId = "1V4MGXIOWhl2uMYjMIDY7LCyHQ429N0A5"
    downloadFolder(service, folderId, destinationFolder)


def downloadFolder(service, fileId, destinationFolder):
    if not os.path.isdir(destinationFolder):
        os.mkdir(path=destinationFolder)

    results = service.files().list(
        pageSize=300,
        q="parents in '{0}'".format(fileId),
        fields="files(id, name, mimeType, fileExtension, size, trashed, trashedTime)",
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True
        ).execute()

    items = results.get('files', [])

    for item in items:
        itemName = item['name']
        itemId = item['id']
        itemType = item['mimeType']
        itemExtension = item['fileExtension'] if 'fileExtension' in item.keys() else ''
        filePath = destinationFolder + "/" + itemName

        if itemType == 'application/vnd.google-apps.folder':
            print("Stepping into folder: {0}".format(filePath))
            downloadFolder(service, itemId, filePath) # Recursive call
        else:
            downloadFile(service, itemName, itemId, itemType, itemExtension, filePath)


def downloadFile(service, itemName, fileId, itemType, itemExtension, filePath):
    # Note: The parent folders in filePath must exist
    print("-> Downloading file with id: {0} name: {1}".format(fileId, filePath))
    itemName = itemName.replace(' ', '').replace(',', '_').replace('/', '_').replace('-','_')
    if itemType == 'application/vnd.google-apps.spreadsheet': #check if not Excel file
        request = service.files().export_media(fileId=fileId, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        request = service.files().get_media(fileId=fileId)

    filePath = os.path.join(destinationFolder, itemName)
    fh = io.FileIO(filePath if itemExtension != '' else filePath +'.xlsx', mode='wb')
    
    try:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk(num_retries = 2)
            if status:
                print("Download %d%%." % int(status.progress() * 100))
        print("Download Complete!")
    finally:
        fh.close()

def concatenate_data():

    merged_df = []
    p = Path(destinationFolder)
    files = p.glob('*.xlsx')
    #Cannot use concat as the files have different headers...
    #df = pd.concat([pd.read_excel(file, usecols='A:W') if len(pd.ExcelFile(file).sheet_names) == 1 else pd.read_excel(file, sheet_name='Template', usecols='A:W') for file in files], sort=False)
    df = [pd.read_excel(file, usecols='A:W') if len(pd.ExcelFile(file).sheet_names) == 1 else pd.read_excel(file, sheet_name='Template', usecols='A:W') for file in files]
    writer = pd.ExcelWriter(r'Downloaded/merged.xlsx', engine='xlsxwriter')
    for data in df:
        for j in range(len(headers)-1):
            data.rename(columns={data.columns[j]: headers[j]}, inplace=True)
            data.dropna(how='all', inplace=True)
    concatenated_data = pd.concat([subset for subset in df])
    concatenated_data.to_excel(writer, index=False, sheet_name='Merged_Data')
    workbook = writer.book
    worksheet = writer.sheets['Merged_Data']
    cell_format = workbook.add_format()
    cell_format.set_num_format(0)
    worksheet.set_column('O:O', None, cell_format)
    writer.save()

#main()
concatenate_data()