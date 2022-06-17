from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
# やりたい処理ごとに権限を設定
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID_OF_JPXINPUT = "1blE4SpoAM-SGhXclosOYVqEwzojvm0x6"
TEST_FILE_NAME = "hello_world.py"


def create_file(file_name: str, folder_id: str, creds) -> None:
    local_file_path = "../test/" + file_name
    try:
        service = build("drive", "v3", credentials=creds)


        # colab/JPX/input
        file_metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(local_file_path, mimetype="text/x-python")
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print("File ID: %s" % file.get("id"))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def update_file(new_file_name: str, file_id: str, creds) -> None:
    new_file_path = "../test/" + new_file_name
    try:
        # First retrieve the file from the API.
        service = build("drive", "v3", credentials=creds)
        file = service.files().get(fileId=file_id).execute()

        # File's new content.
        del file["id"]  # これは必要
        file["name"] = "aaaa.py"
        media_body = MediaFileUpload(new_file_path)

        # Send the request to the API.
        updated_file = (
            service.files()
            .update(
                fileId=file_id,
                body=file,
                media_body=media_body,
            )
            .execute()
        )
        print("File ID: %s" % updated_file.get("id"))
        return updated_file
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    create_file(
        file_name=TEST_FILE_NAME,
        folder_id=FOLDER_ID_OF_JPXINPUT,
        creds=creds,
    )


if __name__ == "__main__":
    main()
