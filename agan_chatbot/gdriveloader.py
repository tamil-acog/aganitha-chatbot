"""Loader that loads data from Google Drive."""

# Prerequisites:
# 1. Create a Google Cloud project
# 2. Enable the Google Drive API:
#   https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com
# 3. Authorize credentials for desktop app:
#   https://developers.google.com/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application # noqa: E501
# 4. For service accounts visit
#   https://cloud.google.com/iam/docs/service-accounts-create
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from googleapiclient.errors import HttpError

from pydantic import BaseModel, root_validator, validator

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class GDriveLoader(BaseLoader, BaseModel):
    """Loader that loads Google Docs from Google Drive."""

    def __init__(self, folder_id: str, shared_dir: str) -> None:
        self.folder_id: Optional[str] = folder_id
        self.shared_dir: str = shared_dir

    service_account_key: Path = Path.home() / ".credentials" / "keys.json"
    credentials_path: Path = Path.home() / ".credentials" / "credentials.json"
    token_path: Path = Path.home() / ".credentials" / "token.json"
    document_ids: Optional[List[str]] = None
    file_ids: Optional[List[str]] = None


    @root_validator
    def validate_folder_id_or_document_ids(
            cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that either folder_id or document_ids is set, but not both."""
        if values.get("folder_id") and (
                values.get("document_ids") or values.get("file_ids")
        ):
            raise ValueError(
                "Cannot specify both folder_id and document_ids nor "
                "folder_id and file_ids"
            )
        if (
                not values.get("folder_id")
                and not values.get("document_ids")
                and not values.get("file_ids")
        ):
            raise ValueError("Must specify either folder_id, document_ids, or file_ids")
        return values

    @validator("credentials_path")
    def validate_credentials_path(cls, v: Any, **kwargs: Any) -> Any:
        """Validate that credentials_path exists."""
        if not v.exists():
            raise ValueError(f"credentials_path {v} does not exist")
        return v

    def _load_credentials(self) -> Any:
        """Load credentials."""
        # Adapted from https://developers.google.com/drive/api/v3/quickstart/python
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            raise ImportError(
                "You must run"
                "`pip install --upgrade "
                "google-api-python-client google-auth-httplib2 "
                "google-auth-oauthlib`"
                "to use the Google Drive loader."
            )

        creds = None
        if self.service_account_key.exists():
            return service_account.Credentials.from_service_account_file(
                str(self.service_account_key), scopes=SCOPES
            )

        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    def _load_sheet_from_id(self, id: str) -> List[Document]:
        """Load a sheet and all tabs from an ID."""

        from googleapiclient.discovery import build

        creds = self._load_credentials()
        sheets_service = build("sheets", "v4", credentials=creds)
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=id).execute()
        sheets = spreadsheet.get("sheets", [])

        documents = []
        for sheet in sheets:
            sheet_name = sheet["properties"]["title"]
            result = (
                sheets_service.spreadsheets()
                    .values()
                    .get(spreadsheetId=id, range=sheet_name)
                    .execute()
            )
            values = result.get("values", [])

            header = values[0]
            for i, row in enumerate(values[1:], start=1):
                metadata = {
                    "source": (
                        f"https://docs.google.com/spreadsheets/d/{id}/"
                        f"edit?gid={sheet['properties']['sheetId']}"
                    ),
                    "title": f"{spreadsheet['properties']['title']} - {sheet_name}",
                    "row": i,
                    "id": id
                }
                content = []
                for j, v in enumerate(row):
                    title = header[j].strip() if len(header) > j else ""
                    content.append(f"{title}: {v.strip()}")

                page_content = "\n".join(content)
                documents.append(Document(page_content=page_content, metadata=metadata))

        return documents

    def _load_slide_from_id(self, id: str) -> List[Document]:
        """Load a sheet and all tabs from an ID."""

        from googleapiclient.discovery import build

        creds = self._load_credentials()
        slide_service = build('slides', 'v1', credentials=creds)
        presentation = slide_service.presentations().get(
            presentationId=id).execute()
        slides = presentation.get('slides')

        documents = []
        for num, slide in enumerate(slides):
            slide_text = []
            slide_page = slide.get('pageElements')
            for content in slide_page:
                text_elements = content.get('shape').get('text').get('textElements')
                for individual_text_elements in text_elements:
                    if 'textRun' in individual_text_elements.keys():
                        text = individual_text_elements.get('textRun').get('content')
                        slide_text.append(text)
            page_content = "\n".join(slide_text)
            metadata = {
                'slide_num': num,
                'id': id
            }
            documents.append(Document(page_content=page_content, metadata=metadata))
        return documents

    def _load_document_from_id(self, id: str) -> Document:
        """Load a document from an ID."""
        from io import BytesIO

        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from googleapiclient.http import MediaIoBaseDownload

        creds = self._load_credentials()
        service = build("drive", "v3", credentials=creds)

        file = service.files().get(fileId=id,fields='name,permissions').execute()
        request = service.files().export_media(fileId=id, mimeType="text/plain")
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        try:
            while done is False:
                status, done = downloader.next_chunk()

        except HttpError as e:
            if e.resp.status == 404:
                print("File not found: {}".format(id))
            else:
                print("An error occurred: {}".format(e))
        text = fh.getvalue().decode("utf-8")
        print('file',file)
        metadata = {
            'permissions': f"{file.get('permissions')}",
            "source": f"https://docs.google.com/document/d/{id}/edit",
            "title": f"{file.get('name')}",
            "id": id
        }
        return Document(page_content=text, metadata=metadata)

    def _load_documents_from_folder(self) -> List[Document]:
        """Load documents from a folder."""
        from googleapiclient.discovery import build

        creds = self._load_credentials()
        service = build("drive", "v3", credentials=creds)

        results = (
            service.files()
                .list(
                q=f"'{self.folder_id}' in parents",
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType)",
            )
                .execute()
        )
        items = results.get("files", [])
        returns = []
        for item in items:
            print('item\n', item)
            if item["mimeType"] == "application/vnd.google-apps.document":
                returns.append(self._load_document_from_id(item["id"]))
            elif item["mimeType"] == "application/vnd.google-apps.spreadsheet":
                returns.extend(self._load_sheet_from_id(item["id"]))
            elif item["mimeType"] == "application/vnd.google-apps.presentation":
                returns.extend(self._load_slide_from_id(item["id"]))
            elif item["mimeType"] == "application/pdf":
                returns.extend(self._load_file_from_id(item["id"]))
            elif item["mimeType"] == "application/vnd.google-apps.folder":
                GDriveLoader(folder_id=item["id"]).load()
            else:
                res = self._unstructured_data_loader(item["id"], item["name"], item["mimeType"])
                if res:
                    returns.extend(res)
        print(returns)
        return returns

    def _unstructured_data_loader(self, id, name, type):

        """Load a file from an ID.
        # # Install package
        !pip install "unstructured[local-inference]"
        !pip install "detectron2@git+https://github.com/facebookresearch/detectron2.git@v0.6#egg=detectron2"
        !pip install layoutparser[layoutmodels,tesseract]

        # # Install other dependencies
        # # https://github.com/Unstructured-IO/unstructured/blob/main/docs/source/installing.rst
        # !brew install libmagic
        # !brew install poppler
        # !brew install tesseract
        # # If parsing xml / html documents:
        # !brew install libxml2
        # !brew install libxslt
        # import nltk
        # nltk.download('punkt')

        """
        from io import BytesIO
        from langchain.document_loaders import UnstructuredFileLoader
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        creds = self._load_credentials()
        try:
            service = build("drive", "v3", credentials=creds)

            # file = service.files().get(fileId=id).execute()
            # if type == 'application/vnd.google-apps.presentation':
            #     print('if')
            #     request = service.files().export_media(fileId=id, mimeType='application/pdf')
            # else:
            request = service.files().get_media(fileId=id)

            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            # data = BytesIO(content)
            print(type)
            if type != 'video/mp4':
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(F'Download {int(status.progress() * 100)}.')
                content = fh.getvalue()
                with open(name, 'wb+') as f:
                    f.write(content)
                print(name)
                loader = UnstructuredFileLoader(name)
                docs = loader.load()
                print(docs)
                return docs
            else:
                if not os.path.exists(self.shared_dir):
                    os.makedirs(self.shared_dir, exist_ok=True)

                if name not in os.listdir(self.shared_dir):
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(F'Download {int(status.progress() * 100)}.')
                    content = fh.getvalue()
                    with open(self.shared_dir + '/' + name, 'wb+') as f:
                        f.write(content)
                    return
                else:
                    print(f'file {name}  in {self.shared_dir} directory already exists skipping')
        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

    def _load_documents_from_ids(self) -> List[Document]:
        """Load documents from a list of IDs."""
        if not self.document_ids:
            raise ValueError("document_ids must be set")

        return [self._load_document_from_id(doc_id) for doc_id in self.document_ids]

    def _load_file_from_id(self, id: str) -> List[Document]:
        """Load a file from an ID."""
        from io import BytesIO

        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        creds = self._load_credentials()
        service = build("drive", "v3", credentials=creds)

        file = service.files().get(fileId=id).execute()
        request = service.files().get_media(fileId=id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        content = fh.getvalue()

        from PyPDF2 import PdfReader

        pdf_reader = PdfReader(BytesIO(content))

        return [
            Document(
                page_content=page.extract_text(),
                metadata={
                    "source": f"https://drive.google.com/file/d/{id}/view",
                    "title": f"{file.get('name')}",
                    "page": i,
                    "id": id
                },
            )
            for i, page in enumerate(pdf_reader.pages)
        ]

    def _load_file_from_ids(self) -> List[Document]:
        """Load files from a list of IDs."""
        if not self.file_ids:
            raise ValueError("file_ids must be set")
        docs = []
        for file_id in self.file_ids:
            docs.extend(self._load_file_from_id(file_id))
        return docs

    def load(self) -> List[Document]:
        """Load documents."""
        if self.folder_id:
            return self._load_documents_from_folder()
        elif self.document_ids:
            return self._load_documents_from_ids()
        else:
            return self._load_file_from_ids()
