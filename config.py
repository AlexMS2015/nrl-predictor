import sys
import os
import yaml
from pathlib import Path
from typing import Optional
from loguru import logger
from pydantic import BaseModel
from utilities.gcs_client import GCSClient
from utilities.path_builder import PathBuilder


class URLConfig(BaseModel):
    main: str
    draw: str

    def draw_url(self, competition_code):
        return f"{self.main}/{self.draw}/?competition={competition_code}"

    def round_url(self, competition_code, round, year):
        return f"{self.main}/{self.draw}/?competition={competition_code}&round={round}&season={year}"


class Config(BaseModel):
    env: str = os.getenv("ENV", "dev")
    buckets: dict[str, str]
    urls: URLConfig
    competition_code_map: dict[str, str]
    feature_pipeline: list[str]
    _gcs_client: Optional[GCSClient] = None
    _paths: Optional[PathBuilder] = None

    @property
    def competition_codes(self):
        return self.competition_code_map.values()

    def comp_code_to_name(self, competition_code):
        codes_reversed = {v: k for k, v in self.competition_code_map.items()}
        return codes_reversed.get(competition_code, None)

    @property
    def bucket(self):
        return self.buckets[self.env]

    @property
    def gcs_client(self):
        if self._gcs_client is None:
            self._gcs_client = GCSClient(bucket=self.bucket)
        return self._gcs_client

    @property
    def paths(self):
        if self._paths is None:
            self._paths = PathBuilder(bucket=self.bucket)
        return self._paths


config_path = Path(__file__).parent / "config.yaml"
with open(config_path, "r") as file:
    config_data = yaml.safe_load(file)

conf = Config(**config_data)

logger_path = Path(__file__).parent / "logs" / "app.log"
logger.remove()
logger.add(logger_path, level="DEBUG")
logger.add(sys.stdout, level="INFO", enqueue=True)
