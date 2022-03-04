import os.path
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from pathlib import Path


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
JSON_creds = 'Bot_Creds.json'
destinationFolder = "Downloaded"
headers= ['Payment Type','Payment Period ID','Email Address','First Name','Last Name',
'Tax Country','Payment Currency Code','Payment Amount','Workday Project ID',
'Workday Project Name','Pmt Method','Bank Name','Institution Number or Swift',
'Routing Transit Number','Bank Account Number','IBAN','Beneficiary Name',
'Address Line 1 for Wire','Address Line 2 for Wire','City for Wire','Province for Wire',
'Country for Wire','Wire Comment for Wire']

def main():
    folderId = input('Give folder ID: ')
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, SCOPES)
    service = build('drive', 'v3', credentials=creds)
    downloadFolder(service, folderId, destinationFolder)
    print('All files downloaded. Merging data')
    concatenate_data()
    print('Merged file available.')

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
    p = Path(destinationFolder)
    files = p.glob('*.xlsx')
    #Cannot use concat as the files have different headers...
    #df = pd.concat([pd.read_excel(file, usecols='A:W') if len(pd.ExcelFile(file).sheet_names) == 1 else pd.read_excel(file, sheet_name='Template', usecols='A:W') for file in files], sort=False)
    dtype_dic= {'Bank Account Number': str, 
            'Routing Transit Number' : str,
            'IBAN' : str,
            'Payment amount': float}
    df = [pd.read_excel(file, usecols='A:W', dtype=dtype_dic) if len(pd.ExcelFile(file).sheet_names) == 1 else pd.read_excel(file, sheet_name='Template', usecols='A:W', dtype=dtype_dic) for file in files]    
    for data in df:
        #Renaming properly all columns by index
        for j in range(len(headers)-1):
            data.rename(columns={data.columns[j]: headers[j]}, inplace=True)
            #Trimming if string, accessing by index
            if data.iloc[:,j].dtype == 'O':
                data.iloc[:,j] = data.iloc[:,j].str.strip()
        #Capitalizing first letters of each word for FN, LN and Beneficiary
        data['First Name'] = data['First Name'].str.title()
        data['Last Name'] = data['Last Name'].str.title()
        data['Beneficiary Name'].fillna('', inplace=True)
        data['Beneficiary Name'] = data['Beneficiary Name'].str.title()
        data.dropna(how='all', inplace=True)
    concatenated_data = pd.concat([subset for subset in df])
    write_report(concatenated_data)

def write_report(concatenated_data):
    writer = pd.ExcelWriter(r'merged.xlsx', engine='xlsxwriter')
    concatenated_data.to_excel(writer, index=False, sheet_name='Merged_Data')
    writer.save()

main()
#concatenate_data()