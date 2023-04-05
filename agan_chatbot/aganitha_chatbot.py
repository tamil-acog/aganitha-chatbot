from agan_chatbot.pipeline import Pipeline
from langchain.llms import OpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
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

    chain = load_qa_with_sources_chain(OpenAI(temperature=0))

    with open("search_index.pickle", "rb") as f:
        search_index = pickle.load(f)

    question: str = str(input("Hi, I am Aganitha's Jarvis. How may I help you?\n"))
    print(
        chain(
            {
                "input_documents": search_index.similarity_search(question, k=3),
                "question": question,
            },
            return_only_outputs=True,
        )["output_text"]
    )


def main():
    app()


