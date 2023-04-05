import moviepy.editor as mp
from typing import List
from langchain.docstore.document import Document
import whisper
import os


class VideoExtractor:
    def __init__(self, video_directory: str):
        self.video_directory = video_directory
        self.audio_directory = None

    def audio_files_generator(self) -> None:
        """ Generates audio files from video files in the directory"""
        os.mkdir(self.video_directory, "audio_files")  # Creating a separate directory for audio files
        self.audio_directory = os.path.join(self.video_directory, "audio_files")
        for file_name in os.listdir(self.video_directory):
            video_file: str = os.path.join(self.video_directory, file_name)
            clip = mp.VideoFileClip(r"{}".format(video_file))
            audio_file: str = os.path.splitext(video_file)[0]
            clip.audio.write_audiofile(r"audio_files/{}.mp3".format(audio_file))

    def transcript_generator(self) -> List[Document]:
        """Using the whisper model, converting the audio to transcript and writing it
           into a pdf and storing them in the knowledge directory"""
        model: whisper = whisper.load_model("small")
        texts: List[str] = []
        docs: List[Document] = []
        for file in os.listdir(self.audio_directory):
            transcription = model.transcribe(file)
            segments = transcription['segments']
            for segment in segments:
                text = segment['text']
                texts.append("".join(text))
            transcript: str = " ".join(texts).strip(" ")
            doc: Document = Document(page_content=transcript)
            docs.append(doc)
        return docs




