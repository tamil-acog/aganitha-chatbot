from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from agan_chatbot.constants import EMBEDDING_MODEL,INDEX_FILE
from langchain.vectorstores import FAISS
from agan_chatbot import gdrive_extractor, video_extractor, website_extractor, knowlede_directory_extractor
from typing import List
import pickle
import logging
import warnings

warnings.filterwarnings("ignore")
logging.basicConfig(level='INFO')


class Pipeline:
    def __init__(self, web_input_file: str, video_directory: str, knowledge_directory: str, folder_id: str):
        self.web_input_file = web_input_file
        self.video_directory = video_directory
        self.knowledge_directory = knowledge_directory
        self.folder_id = folder_id
        self.splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
        self.source_docs = []
        self.source_chunks: List = []
        self.embeddings: object = EMBEDDING_MODEL
        self.search_index: object = None

    def __call__(self):
        logging.info("Pipeline called")
        # Calling the website pipeline
        website_docs = website_extractor.WebsiteExtractor.website_loader(self.web_input_file)

        # Calling the knowledge_directory pipeline
        knowledge_directory_docs = knowlede_directory_extractor.KnowledgeDirectoryExtractor.\
            directory_loader(self.knowledge_directory)

        # Calling the gdrive pipeline
        # gdrive_docs = gdrive_extractor.GdriveExtractor.gdrive_knowledge_extractor(self.folder_id)

        # Calling the video_extractor pipeline
        video_knowledge = video_extractor.VideoExtractor(self.video_directory)
        video_docs = video_knowledge()

        self.source_docs = website_docs + video_docs + knowledge_directory_docs
        self.create_index(self.source_docs)
        return

    def create_index(self, docs) -> None:
        logging.info("create_index called")
        for doc in docs:
            for chunk in self.splitter.split_text(doc.page_content):
                self.source_chunks.append(Document(page_content=chunk, metadata=doc.metadata))

        self.search_index = FAISS.from_documents(self.source_chunks, self.embeddings)
        with open(INDEX_FILE, "wb") as f:
            pickle.dump(self.search_index, f)
        logging.info("search_index created")
        return

