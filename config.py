import sys
import yaml
from loguru import logger
from pydantic import BaseModel
from pathlib import Path


class Config(BaseModel):
    gcs_bucket: dict[str, str]
    competition_codes: dict[str, str]
    feature_pipeline: list[str]

    def comp_code_to_name(self, competition_code):
        codes_reversed = {v: k for k, v in self.competition_codes.items()}
        return codes_reversed.get(competition_code, None)


config_path = Path(__file__).parent / "config.yaml"
with open(config_path, "r") as file:
    config_data = yaml.safe_load(file)

config = Config(**config_data)

logger_path = Path(__file__).parent / "logs" / "app.log"
logger.remove()
logger.add(logger_path, level="DEBUG")
logger.add(sys.stdout, level="INFO", enqueue=True)
