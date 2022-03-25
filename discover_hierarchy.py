from googleapiclient.discovery import build
from apiclient import errors
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import errors


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
JSON_creds = 'Bot_Creds.json'

def main():
    folderId = input('Give folder ID: ')
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_creds, SCOPES)
    service = build('drive', 'v3', credentials=creds)
    list_files = downloadFolder(service, folderId)
    permissions_found = retrieve_permissions(service, list_files)

def downloadFolder(service, fileId):

    results = service.files().list(
        pageSize=300,
        q="parents in '{0}'".format(fileId),
        fields="files(id, name, mimeType, fileExtension, size, trashed, trashedTime, lastModifyingUser, permissions)",
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True
        ).execute()

    files = results.get('files', [])
    return(files)

def retrieve_permissions(service, files):
  """Retrieve a list of permissions.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to retrieve permissions for.
  Returns:
    List of permissions.
  """
  for file in files:
    permissions = service.permissions().list(fileId=file['id'],
        fields='*',
        supportsAllDrives=True).execute()
    
main()