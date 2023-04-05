from langchain.document_loaders import DirectoryLoader
from typing import List


class KnowledgeDirectoryExtractor:

    @staticmethod
    def directory_loader(knowledge_directory: str) -> List:
        """Loads all the files from the directory using Unstructured Loader class under the hood"""
        loader: DirectoryLoader = DirectoryLoader(knowledge_directory + '/')
        docs: List = loader.load()
        return docs
