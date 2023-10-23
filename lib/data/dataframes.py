import os
from collections import namedtuple
from typing import List
import pandas as pd


class Frame:
    def __init__(
        self,
        name: str,
        headers: List[str],
        path: str,
    ) -> None:
        self.name = name
        self.headers = headers
        self.path = path
        self.df = pd.DataFrame(columns=self.headers)
        
        self.full_path = ""

    def add_row(self, data: namedtuple) -> None:
        self.df = self.df.append(data._asdict(), ignore_index=True)

    def load(self) -> None:
        if os.path.exists(self.full_path):
            self.df = pd.read_csv(self.full_path)
        else:
            self.df = self.df

    def save(self) -> None:
        self.df.to_csv(self.full_path, index=True)

    def reset(self) -> None:
        self.df = pd.DataFrame(columns=self.headers)

    def set_filename(self, suffix: str) -> None:
        self.full_path = self.path + suffix + ".csv"

