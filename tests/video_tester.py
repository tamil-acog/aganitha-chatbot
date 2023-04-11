from agan_chatbot.video_extractor import VideoExtractor

video_knowledge = VideoExtractor("/own4lake/tamil/videos")
video_docs = video_knowledge()
print(video_docs)
