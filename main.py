import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
    """Deletes all files in Google Drive and empties the trash."""
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "creds.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)

        # List all files in the Drive
        results = (
            service.files()
            .list(pageSize=1000, fields="nextPageToken, files(id)")
            .execute()
        )
        items = results.get("files", [])

        # Delete all files
        for item in items:
            service.files().delete(fileId=item["id"]).execute()
            print(f"Deleted file with ID: {item['id']}")

        # Empty the trash
        service.files().emptyTrash().execute()
        print("Trash emptied.")
    except HttpError as error:
        # Handle errors from Drive API
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
