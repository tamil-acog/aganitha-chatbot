import moviepy.editor as mp
from typing import List
import whisper
import os


class VideoExtracter:
    def __init__(self, directory: str, knowledge_directory: str):
        self. directory = directory
        self.knowledge_directory = knowledge_directory
        self.audio_directory = None

    def audio_files_generator(self) -> None:
        """ Generates audio files from video files in the directory"""
        os.mkdir(self.directory, "audio_files")  # Creating a separate directory for audio files
        self.audio_directory = os.path.join(self.directory, "audio_files")
        for file_name in os.listdir(self.directory):
            video_file: str = os.path.join(self.directory, file_name)
            clip = mp.VideoFileClip(r"{}".format(video_file))
            audio_file: str = os.path.splitext(video_file)[0]
            clip.audio.write_audiofile(r"audio_files/{}.mp3".format(audio_file))

    def transcript_generator(self) -> None:
        """Using the whisper model, converting the audio to transcript and writing it
           into a pdf and storing them in the knowledge directory"""
        model: whisper = whisper.load_model("small")
        texts: List[str] = []
        for file in os.listdir(self.audio_directory):
            transcription = model.transcribe(file)
            segments = transcription['segments']
            for segment in segments:
                text = segment['text']
                texts.append("".join(text))
            transcript: str = " ".join(texts).strip(" ")
            with open(os.path.join(self.knowledge_directory, os.path.splitext(file)[0] + ".pdf"), "wb") as f:
                f.write(transcript)





