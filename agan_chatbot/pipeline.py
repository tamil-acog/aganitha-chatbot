from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from agan_chatbot import video_extractor, website_extractor, knowlede_directory_extractor
from agan_chatbot.yaml_parser import YamlParser
from typing import List, Any
import pickle
import logging
import warnings
from agan_chatbot.gdrive_extractor import GDriveLoader

warnings.filterwarnings("ignore")
logging.basicConfig(level='INFO')


class Pipeline:
    def __init__(self, web_input_file: str = None, video_directory: str = None, knowledge_directory: str = None, folder_id: str = None):
        self.web_input_file = web_input_file
        self.video_directory = video_directory
        self.knowledge_directory = knowledge_directory
        self.folder_id = folder_id
        self.splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
        self.source_docs = []
        self.source_chunks: List = []
        self.yaml_loader: object = YamlParser()
        self.yaml_loader()
        self.vectordb: str = self.yaml_loader.vectordb
        self.embed_model: str = self.yaml_loader.embed_model
        self.embeddings = None
        self.search_index = None
        self.vector_db = None

    def __call__(self):
        logging.info("Pipeline called")

        # Calling the gdrive pipeline
        gdrive = GDriveLoader(folder_id=self.folder_id, shared_dir=self.video_directory)
        gdrive_docs = gdrive.load()

        # Calling the website pipeline
        website_docs = website_extractor.WebsiteExtractor.website_loader(self.web_input_file)

        # Calling the knowledge_directory pipeline
        knowledge_directory_docs = knowlede_directory_extractor.KnowledgeDirectoryExtractor.\
            directory_loader(self.knowledge_directory)
        
        # Calling the video_extractor pipeline. It depends on the gdrive pipeline
        video_knowledge = video_extractor.VideoExtractor(self.video_directory)
        video_docs = video_knowledge()

        self.source_docs = gdrive_docs + website_docs + video_docs + knowledge_directory_docs
        self.create_chunks(self.source_docs)
        return

    def create_chunks(self, docs) -> None:
        logging.info("chunks are being created")
        for doc in docs:
            for chunk in self.splitter.split_text(doc.page_content):
                self.source_chunks.append(Document(page_content=chunk, metadata=doc.metadata))

        print(self.embed_model)
        self._select_embeddings(self.embed_model)
        print(self.vectordb)
        self._select_index(self.vectordb)

    def _select_index(self, vectordb: str) -> Any:
        if vectordb == "FAISS":
            return self.faiss_index(self.source_chunks)

        if vectordb == "MILVUS":
            print("MILVUS called")
            return self.milvus_index(self.source_chunks)

    def _select_embeddings(self, embed_model: str) -> Any:
        if embed_model == "OPENAI":
            from langchain.embeddings.openai import OpenAIEmbeddings
            self.embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

        # if embed_model == "BioMedGPT":
        #     self.embeddings: BioMed = BioMedEmbedding

    def faiss_index(self, docs) -> None:
        quit()
        from langchain.vectorstores import FAISS
        search_index = FAISS.from_documents(docs, self.embeddings)
        with open("search_index.pickle", "wb") as f:
            pickle.dump(search_index, f)
        logging.info("FAISS search_index created")
        return

    def milvus_index(self, docs) -> None:
        from langchain.vectorstores import Milvus
        vector_db = Milvus.from_documents(docs,
                                          self.embeddings,
                                          connection_args={"alias": "default", 
                                          "uri": "https://in01-84cae738bde3a79.aws-us-west-2.vectordb.zillizcloud.com:19541",
                                          "secure": True, "user": "db_admin", "password": "guNagaNa1"},
                                          )
        logging.info("MILVUS index created")
    




