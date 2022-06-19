from __future__ import print_function

import os
import shlex
import subprocess
from typing import List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
# やりたい処理ごとに権限を設定
SCOPES = ["https://www.googleapis.com/auth/drive"]
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
GITHUB_WORKSPACE = os.environ.get("GITHUB_WORKSPACE")


def upload_directory_via_gdrive(
    local_directory_path: str, remote_parent_directory_id: str
) -> None:
    cmd = f"gdrive --service-account credential.json upload -r -p {remote_parent_directory_id} {local_directory_path}"
    tokens = shlex.split(cmd)
    subprocess.run(tokens)


# 自分がオーナーであるものしか削除できない
def delete_directory_via_gdrive(remote_directory_id: str) -> None:
    cmd = f"gdrive --service-account credential.json delete -r {remote_directory_id}"
    tokens = shlex.split(cmd)
    subprocess.run(tokens)


def update_directory(
    local_directory_name: str, remote_parent_directory_id: str, creds
) -> None:
    local_directory_path = f"{GITHUB_WORKSPACE}/" + local_directory_name
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
        GOOGLE_APPLICATION_CREDENTIALS
    )

    scoped_creds = creds.with_scopes(SCOPES)

    GitHub_actions_tutorial_id = file_name2ids(
        file_name="GitHub_actions_tutorial", creds=scoped_creds
    )[0]

    update_directory(
        local_directory_name="test",
        remote_parent_directory_id=GitHub_actions_tutorial_id,
        creds=scoped_creds,
    )


if __name__ == "__main__":
    main()
