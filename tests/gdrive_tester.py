from agan_chatbot.gdrive_extractor import GDriveLoader


gdrive_docs = GDriveLoader(folder_id="10Fi-DP40MZQi9olH_fOeTGh-A3JD7KVC", shared_dir="/own4lake/sezaz/chatbot/videos")
docs = gdrive_docs.load()
print(docs)