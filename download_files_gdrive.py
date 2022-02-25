import os.path
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
JSON_creds = 'Bot_Creds.json'
destinationFolder = "Downloaded"

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
        fields="files(id, name, mimeType)",
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True
        ).execute()

    items = results.get('files', [])

    for item in items:
        itemName = item['name']
        itemId = item['id']
        itemType = item['mimeType']
        filePath = destinationFolder + "/" + itemName

        if itemType == 'application/vnd.google-apps.folder':
            print("Stepping into folder: {0}".format(filePath))
            downloadFolder(service, itemId, filePath) # Recursive call
        else:
            downloadFile(service, itemName, itemId, itemType, filePath)


def downloadFile(service, itemName, fileId, itemType, filePath):
    # Note: The parent folders in filePath must exist
    print("-> Downloading file with id: {0} name: {1}".format(fileId, filePath))
    itemName = itemName.replace(' ', '').replace(',', '_').replace('/', '_').replace('-','_')
    if itemType == 'application/vnd.google-apps.spreadsheet': #check if not Excel file
        request = service.files().export_media(fileId=fileId, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        request = service.files().get_media(fileId=fileId)
    filePath = os.path.join(destinationFolder, itemName)
    fh = io.FileIO(filePath if 'xlsx' in filePath else filePath +'.xlsx', mode='wb')
    
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

main()