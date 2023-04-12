from aganitha_chatbot_pipeline.pipeline import Pipeline
import typer

app = typer.Typer()

@app.command()
def run_pipeline(web_input_file: str = typer.Argument(None), video_directory: str = typer.Argument(None),
                 knowledge_directory: str = typer.Argument(None), folder_id: str = typer.Argument(None)):
    """ Pipeline is called which pulls the data from all the resources we specify"""
    pipeline = Pipeline(web_input_file, video_directory, knowledge_directory, folder_id)
    pipeline()


def main():
    app()


if __name__ == "__main__":
    app()

