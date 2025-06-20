from pydantic import BaseModel
import yaml
import os

class Config(BaseModel):
    gcs_bucket: dict[str, str]
    
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

    competition: dict[str, str]

with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)
    
config = Config(**config_data)