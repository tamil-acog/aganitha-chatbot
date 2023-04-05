from langchain.document_loaders import GoogleDriveLoader
from typing import List


class GdriveExtractor:

    @staticmethod
    def gdrive_knowledge_extractor(folder_id: str) -> List:
        """This will load files of type google docs, websites, videos and return the document objects"""
        loader = GoogleDriveLoader(folder_id=folder_id)
        docs: List = loader.load()
        return docs
