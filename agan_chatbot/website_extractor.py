from langchain.document_loaders import WebBaseLoader
from typing import List


class WebsiteExtractor:

    @staticmethod
    def website_loader(web_input_file: str) -> List:
        """Takes in a file with list of links and returns the contents of the
           websites as document objects"""
        with open(web_input_file, "rb") as f:
            urls = [line.strip() for line in f]

        loader = WebBaseLoader(urls)
        docs = loader.load()
        return docs
