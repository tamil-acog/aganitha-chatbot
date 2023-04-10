import yaml


class YamlParser:
    """This class parses the Yaml configure file and sends the Yaml data"""
    def __init__(self):
        self.vectordb: str = ""
        self.embed_model: str = ""
        self.yaml_file: str = "config.yml"

    def __call__(self, *args, **kwargs)-> None:
        with open(self.yaml_file) as fp:
            yaml_data: list[str] = yaml.safe_load(fp)
        self.vectordb = yaml_data["VECTORDB"]
        self.embed_model = yaml_data["EMBEDDING"]
