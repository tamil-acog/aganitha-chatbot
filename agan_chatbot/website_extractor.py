from langchain.document_loaders import WebBaseLoader
from typing import List


class WebsiteExatractor:

    @staticmethod
    def website_loader(input_file: str) -> List:
        with open(input_file, "rb") as f:
            urls = [line.strip() for line in f]

        loader = WebBaseLoader(urls)
        docs = loader.load()
        return docs
