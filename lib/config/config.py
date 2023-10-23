import yaml
from config.recursive_namespace import RecursiveNamespace


class Config(RecursiveNamespace):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def from_file(cls, path: str):
        with open(path) as file:
            config_yaml = yaml.safe_load(file)
            if config_yaml is None:
                config_yaml = {}
        self = cls()
        self.update(config_yaml)
        return self

    def save(self, path: str) -> None:
        with open(path, 'w') as file:
            yaml.safe_dump(self.to_dict(), file)

