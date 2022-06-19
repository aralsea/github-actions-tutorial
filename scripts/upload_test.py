from __future__ import print_function

import os
import shlex
import subprocess
from typing import List, Optional

import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
# やりたい処理ごとに権限を設定
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID_OF_JPXSRC = "1gOZ_kqSEn0jnAYa9GTnfdrFyW92j1jDs"
TEST_FILE_NAME = "hello_world.py"
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


def create_file(file_name: str, folder_id: str, creds) -> None:
    local_file_path = "../test/" + file_name
    try:
        service = build("drive", "v3", credentials=creds)
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


def upload_directory_via_gdrive(
    local_directory_path: str, remote_parent_directory_id: str
):
    cmd = f"gdrive --service-account credential.json upload -r -p {remote_parent_directory_id} {local_directory_path}"
    tokens = shlex.split(cmd)
    subprocess.run(tokens)


# 自分がオーナーであるものしか削除できない
def delete_directory_via_gdrive(remote_directory_id: str):
    cmd = f"gdrive --service-account credential.json delete -r {remote_directory_id}"
    tokens = shlex.split(cmd)
    subprocess.run(tokens)


def update_directory(local_directory_name: str, remote_parent_directory_id: str, creds):
    local_directory_path = "../" + local_directory_name
    remote_directory_ids = file_name2ids(
        file_name=local_directory_name,
        remote_parent_directory_id=remote_parent_directory_id,
        creds=creds,
    )

    for remote_directory_id in remote_directory_ids:
        delete_directory_via_gdrive(remote_directory_id=remote_directory_id)
    upload_directory_via_gdrive(
        local_directory_path=local_directory_path,
        remote_parent_directory_id=remote_parent_directory_id,
    )


def file_name2ids(
    file_name: str,
    creds,
    remote_parent_directory_id: Optional[str] = None,
) -> List[str]:
    drive_service = build("drive", "v3", credentials=creds)
    query = "trashed = False"
    if remote_parent_directory_id:
        query += f" and parents in {remote_parent_directory_id}"
    response = (
        drive_service.files()
        .list(
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields="nextPageToken, files(id, name)",
        )
        .execute()
    )
    files = response.get("files", [])  # 辞書のリスト

    results: List[str] = []
    for file in files:
        if file.get("name") == file_name:
            results.append(file.get("id"))

    return results


def main():
    # creds, project = google.auth.default()
    creds = service_account.Credentials.from_service_account_file(
        "credentials2.json"
    )

    scoped_creds = creds.with_scopes(SCOPES)

    print(file_name2ids(file_name="test", creds=scoped_creds))

    GitHub_actions_tutorial_id = file_name2ids(
        file_name="GitHub_actions_tutorial", creds=scoped_creds
    )[0]

    update_directory(
        local_directory_name="test",
        remote_parent_directory_id=GitHub_actions_tutorial_id,
        creds=scoped_creds,
    )
    """create_file(
        file_name=TEST_FILE_NAME,
        folder_id=FOLDER_ID_OF_JPXSRC,
        creds=scoped_creds,
    )"""

    """update_file("test2.py", "1-DKP11Xmdb5vwcQ-rkRo6Ak0xnwH9KAC", scoped_creds)"""


if __name__ == "__main__":
    main()
