from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import GoogleDriveLoader
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from typing import List
import pickle


class Pipeline:
    def __init__(self, folder_id: str):
        self.folder_id = folder_id
        self.splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
        self.source_chunks: List = []
        self.embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
        self.search_index: object = None

    def __call__(self):
        print("Pipeline called")
        self.gdrive_knowledge_extractor(self.folder_id)
        return

    def gdrive_knowledge_extractor(self, folder_id) -> None:
        print("Knowledge_extractor called")
        loader = GoogleDriveLoader(folder_id=folder_id)
        source_docs: List[Document] = loader.load()
        print(source_docs)
        print(len(source_docs))
        self.create_index(source_docs)
        return

    def create_index(self, docs) -> None:
        print("create_index called")
        for doc in docs:
            for chunk in self.splitter.split_text(doc.page_content):
                self.source_chunks.append(Document(page_content=chunk, metadata=doc.metadata))

        self.search_index = FAISS.from_documents(self.source_chunks, self.embeddings)
        with open("search_index.pickle", "wb") as f:
            pickle.dump(self.search_index, f)
        return

