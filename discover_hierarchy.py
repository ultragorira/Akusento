from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import csv


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
JSON_creds = 'Bot_Creds.json'
HEADERS = ['FILENAME', 'FILE ID', 'NAME', 'EMAIL', 'ROLE']
data = []

def main():
    folderId = input('Give folder ID: ')
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, SCOPES)
    service = build('drive', 'v3', credentials=creds)
    searchFolder(service, folderId)
    write_report(data)

def searchFolder(service, fileId):

    results = service.files().list(
        pageSize=300,
        q="parents in '{0}'".format(fileId),
        fields="files(id, name, mimeType, fileExtension, size, trashed, trashedTime, lastModifyingUser, permissions)",
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True
        ).execute()

    files = results.get('files', [])

    for file in files:
      if file['mimeType'] == 'application/vnd.google-apps.folder':
        searchFolder(service, file['id']) #Recursively checking other subfolders
      else:
        #print(file['id'])
        retrieve_permissions(service, file['id'], file['name'])

def retrieve_permissions(service, file_id, file_name):
  """Retrieve a list of permissions.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to retrieve permissions for.
  Returns:
    List of permissions.
  """
  permissions = service.permissions().list(fileId=file_id,
        fields='*',
        supportsAllDrives=True).execute()
  try: 
    for permission in permissions['permissions']:
      if 'youroppa' not in permission['displayName']: #This is the bot name
        try:
          data.append([file_name, file_id, permission['displayName'], permission['emailAddress'],permission['role']])
        except Exception:
          print(f'Could not retrieve info on {file_id}')
      else:
        continue
  except Exception as e:
    print(e)
      #print(permission)  

def write_report(data):

    with open('Report.csv', mode='w', newline='', encoding='utf-8-sig') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(HEADERS)
        csv_writer.writerows(data)


main()