from agan_chatbot.pipeline import Pipeline
from agan_chatbot.constants import INDEX_FILE
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
import typer
import pickle

app = typer.Typer()


@app.command()
def answer_the_query(web_input_file: str = typer.Argument(None), video_directory: str = typer.Argument(None),
                     knowledge_directory: str = typer.Argument(None), folder_id: str = typer.Argument(None),
                     pipeline: str = typer.Argument(None)):

    if pipeline == "yes":
        print("I am going to call Pipeline")
        pipeline = Pipeline(web_input_file, video_directory, knowledge_directory, folder_id)
        pipeline()
        

    with open(INDEX_FILE, "rb") as f:
        search_index = pickle.load(f)
    
    vectorestore = search_index

    chain = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0),vectorestore.as_retriever(),return_source_documents=True)


    chat_history = []
    for i in range(0,3):
        if i == 0:
            question: str = str(input("Hi, I am Aganitha's Jarvis. How may I help you?\n"))
        else:
            question: str = str(input("\nPlease enter your follow-up question:"))
        result: object = chain({ "question": question,"chat_history": chat_history})   
        answer: str = result['answer']

        chat_history.append((question,answer))
        
        source: str = result['source_documents'] 
        sources=[]
        for i in range(0, len(source)):
            sources.append(source[i].metadata['source'])

        print("\n\n",answer,"\n\nThe source of information are:",sources)

    print("\nThank you for talking to Aganitha's Jarvis.")



def main():
    app()


