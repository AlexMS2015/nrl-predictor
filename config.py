import sys
import yaml
from loguru import logger
from pydantic import BaseModel


class Config(BaseModel):
    teams: list[str]

    nrl_website: str
    nrlw_website: str
    hostplus_website: str
    knockon_website: str

    player_labels: list[str]
    nrl_2024_round: int

    team_colours: dict[str, str]
    team_colours_inverse: dict[str, str]

    nrlw_teams: list[str]
    hostplus_teams: list[str]
    knockon_teams: list[str]

    competition_codes: dict[str, str]

    def comp_code_to_name(self, competition_code):
        codes_reversed = {v: k for k, v in self.competition_codes.items()}
        return codes_reversed.get(competition_code, None)


with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

config = Config(**config_data)

logger.remove()
logger.add("app.log", level="DEBUG")
logger.add(sys.stdout, level="INFO", enqueue=True)
