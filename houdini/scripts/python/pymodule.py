import os
import os.path
import ctypes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


PRJ_ROOT = os.getenv("HIP")
PRJ_NAME = os.path.basename(PRJ_ROOT)
GDRIVE_LOCAL_PRIVATE = f"{PRJ_ROOT}/.gdrive"
if not os.path.exists(GDRIVE_LOCAL_PRIVATE):
        os.makedirs(GDRIVE_LOCAL_PRIVATE)
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ret = ctypes.windll.kernel32.SetFileAttributesW(GDRIVE_LOCAL_PRIVATE, FILE_ATTRIBUTE_HIDDEN)
GDRIVE_TOKEN_PATH = f"{GDRIVE_LOCAL_PRIVATE}/token.json"
GDRIVE_CREDENTIAL_PATH = f"{GDRIVE_LOCAL_PRIVATE}/credentials.json"
GDRIVE_ROOT = "PROJECTS_backupFiles"


class GDUploader():
    '''
        Google Drive Uploader class.
        Builds the proper folder structure and connection with Google Drive.
        Each file gets backed-up during the post-write script from the internal file_cache node.
    '''
    __SCOPES = ["https://www.googleapis.com/auth/drive"]
    
    def __init__(self, data_folder) -> None:
        self.__creds = None
        self.data_folder = data_folder

        self.authenticate()
        self.setDriveFolders()

    def authenticate(self) -> None:
        '''
            Authentication required for Google Drive connection
        '''
        if os.path.exists(GDRIVE_TOKEN_PATH):
            self.__creds = Credentials.from_authorized_user_file(GDRIVE_TOKEN_PATH, self.__SCOPES)

        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(GDRIVE_CREDENTIAL_PATH, self.__SCOPES)
                self.__creds = flow.run_local_server(port=0)

            with open(GDRIVE_TOKEN_PATH, "w") as token:
                token.write(self.__creds.to_json())

    def setDriveFolders(self) -> None:
        '''
            Building and gathering correct folder structure based on internal file_cache
        '''
        _extra_folders = os.path.relpath(self.data_folder, start=PRJ_ROOT)
        folders_list = [GDRIVE_ROOT, PRJ_NAME]
        folders_list += _extra_folders.split("\\")

        try:
            self.service = build("drive", "v3", credentials=self.__creds)

            # Gather Google Drive root id
            parent = self.service.files().get(fileId='root').execute()['id']

            # Loop through all folder_lists. Check if folders exists. If not create them
            for folder in folders_list:
                response = self.service.files().list(
                    q=f"name='{folder}' and mimeType='application/vnd.google-apps.folder'",
                    spaces='drive',
                    fields="nextPageToken, files(id, name, parents, mimeType)",
                ).execute()

                
                # The response form Google Drive will contain all the folders matching the specified name.
                # Making sure the folder parent is equal to the current parent in loop.
                folder_lookup = None
                for file in response['files']:
                     if parent == file["parents"][0]:
                          folder_lookup = file
                          break

                if not folder_lookup:
                    file_metadata = {
                        "name": f'{folder}',
                        "mimeType": "application/vnd.google-apps.folder",
                        "parents": [parent]
                    }

                    # Create folder in Drive
                    file = self.service.files().create(body=file_metadata, fields="id").execute()
                    self.folder_id = file.get("id")

                    print (f"GDrive: {folder} folder created")
                else:
                    # Gather existing folder in Drive
                    self.folder_id = folder_lookup["id"]
                    print (f"GDrive: {folder} folder found")

                parent = self.folder_id
                
        except HttpError as e:
            print("Error: " + str(e))

    def upload(self, file) -> None:
            '''
                Uploading the file passed as argument to the folder structure created inside the Drive
                during initialization
            '''
            file_name = os.path.basename(file)
            
            file_metadata = {
                "name": file_name,
                "parents": [self.folder_id]
            }

            media = MediaFileUpload(file, resumable=True)
            upload_file = self.service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields="id").execute()
            print("Upload Successfull. File: " + file_name)