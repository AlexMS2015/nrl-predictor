"""
Script to run the data scraper for match and player data.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from config import config as conf
from scraping.utilities.get_nrl_data import get_nrl_data
from utilities.gcs_client import GCSClient

load_dotenv() # for local development. env is injected in production.

competition = os.getenv("TARGET_COMPETITION", "nrl")
min_year = int(os.getenv("MIN_YEAR", 2001))
max_year = int(os.getenv("MAX_YEAR", 2024))
max_round = int(os.getenv("MAX_ROUND", 33))
env = os.getenv("ENV", "dev")
gcs_bucket = conf.gcs_bucket[env]
gcs_client = GCSClient(bucket_name=gcs_bucket)

for year in range(min_year, max_year + 1):
    for round_num in range(1, max_round + 1):
        try:
            competition_code = conf.competition[competition]
        except (TypeError, KeyError):
            print(f"Unknown Competition Type: {competition}")

        print(f"Fetching data for {competition} {year}, {round_num}...")

        match_json = get_nrl_data(round_num, year, competition_code)

        script_dir = Path(__file__).parent
        data_dir = script_dir / "../data" / competition / "match_data"
        data_dir = data_dir.resolve() # convert to absolute path
        data_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{year}_r{round_num}.json"
        file_path = data_dir / file_name
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(match_json, file, ensure_ascii=False, indent=4)#, separators=(',', ':'))
        except Exception as e:
            print(f"Error writing file: {e}")

        gcs_client.upload_to_gcs(
            src_file=str(file_path),
            dest_blob=f"{competition}/match_data/{file_name}"
        )