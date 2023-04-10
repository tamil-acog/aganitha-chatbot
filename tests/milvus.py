from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Milvus
from langchain.document_loaders import TextLoader

loader = TextLoader('/Users/tamil/Downloads/code_breaker.txt')
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

vector_db = Milvus.from_documents(
    docs,
    embeddings,
    connection_args={"alias": "default", "uri": "https://in01-84cae738bde3a79.aws-us-west-2.vectordb.zillizcloud.com:19541",
                     "secure": True, "user": "db_admin", "password": "guNagaNa1"},
)

query = "Who is Isaacson?"

docs = vector_db.similarity_search(query)

print(docs[0])
