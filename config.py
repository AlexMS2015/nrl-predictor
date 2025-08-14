import sys
import os
import yaml
from loguru import logger
from pydantic import BaseModel
from pathlib import Path


class URLConfig(BaseModel):
    main: str
    draw: str

    def draw_url(self, competition_code):
        return f"{self.main}/{self.draw}/?competition={competition_code}"

    def round_url(self, competition_code, round, year):
        return f"{self.main}/{self.draw}/?competition={competition_code}&round={round}&season={year}"


class Config(BaseModel):
    env: str = os.getenv("ENV", "dev")
    gcs_buckets: dict[str, str]
    urls: URLConfig
    competition_code_map: dict[str, str]
    feature_pipeline: list[str]

    @property
    def competition_codes(self):
        return self.competition_code_map.values()

    def comp_code_to_name(self, competition_code):
        codes_reversed = {v: k for k, v in self.competition_code_map.items()}
        return codes_reversed.get(competition_code, None)

    @property
    def gcs_bucket(self):
        return self.gcs_buckets[self.env]


class PathBuilder:
    def __init__(self, gcs_bucket):
        self.bucket = gcs_bucket
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def match_filename(self, round_num, year):
        return f"{year}_r{round_num}.json"

    def blob_path(self, competition, data_type, file_name):
        return "/".join([competition, data_type, file_name])

    def gcs_path(self, blob_path):
        return f"gs://{self.bucket}/{blob_path}"

    def local_path(self, blob_path):
        local_path = self.data_dir / blob_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        return local_path

    # ---- High-level helpers ----
    # def local_match_path(self, competition, year, round_num):
    #     """Full local path for a match JSON file."""
    #     file_name = self.match_filename(round_num, year)
    #     blob = self.blob_path(competition, "match", file_name)
    #     p = self.local_path(blob)
    #     p.parent.mkdir(parents=True, exist_ok=True)
    #     return p

    # def gcs_match_path(self, competition, year, round_num):
    #     """Blob path for GCS upload (relative to bucket)."""
    #     file_name = self.match_filename(round_num, year)
    #     return self.blob_path(competition, "match", file_name)


config_path = Path(__file__).parent / "config.yaml"
with open(config_path, "r") as file:
    config_data = yaml.safe_load(file)

conf = Config(**config_data)
paths = PathBuilder(conf.gcs_bucket)

logger_path = Path(__file__).parent / "logs" / "app.log"
logger.remove()
logger.add(logger_path, level="DEBUG")
logger.add(sys.stdout, level="INFO", enqueue=True)
