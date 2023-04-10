import moviepy.editor as mp
from typing import List
from langchain.docstore.document import Document
import whisper
import os
import subprocess


class VideoExtractor:
    def __init__(self, video_directory: str):
        self.video_directory = video_directory
        self.audio_directory = None

    def __call__(self):
        docs = self.audio_files_generator()
        return docs

    def audio_files_generator(self) -> List[Document]:
        """ Generates audio files from video files in the directory"""
        video_parent = os.path.dirname(self.video_directory)
        if not os.path.exists(os.path.join(video_parent, "audio_files")):
            # Creating a separate directory for audio files
            print(os.path.join(video_parent, "audio_files"))
            os.mkdir(os.path.join(video_parent, "audio_files"))
        self.audio_directory = os.path.join(video_parent, "audio_files")
        for file_name in os.listdir(self.video_directory):
            if file_name.split('.')[-1] in ["m4a", "flac", "mp3", "wav", "wma", "aac"]:
                continue
            video_file: str = os.path.join(self.video_directory, file_name)
            clip = mp.VideoFileClip(r"{}".format(video_file))
            audio_file: str = os.path.splitext(video_file)[0]
            clip.audio.write_audiofile(r"{}.mp3".format(os.path.join(self.audio_directory, audio_file)))
        return self.transcript_generator()

    def transcript_generator(self) -> List[Document]:
        """Using the whisper model, converting the audio to transcript and writing it
           into a pdf and storing them in the knowledge directory"""
        vf = self.video_directory + '/*.mp3'
        af = self.audio_directory
        cmd = "mv {} {}".format(vf, af)
        os.system(cmd)
        model: whisper = whisper.load_model("small")
        texts: List[str] = []
        docs: List[Document] = []
        for file in os.listdir(self.audio_directory):
            transcription = model.transcribe(os.path.join(self.audio_directory,file))
            segments = transcription['segments']
            for segment in segments:
                text = segment['text']
                texts.append("".join(text))
            transcript: str = " ".join(texts).strip(" ")
            id_file = file.split('**')[0]
            doc: Document = Document(page_content=transcript, metadata={"source": os.path.join(self.audio_directory, file),'id':id_file})
            docs.append(doc)
        return docs





