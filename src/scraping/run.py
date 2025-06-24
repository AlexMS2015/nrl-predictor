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
from scraping.utilities.set_up_driver import set_up_driver
from urllib.parse import urlparse, parse_qs
import time


def get_final_url(url):
    driver = set_up_driver()
    driver.get(url)
    time.sleep(3)
    return driver.current_url


def parse_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return {
        'competition_code': query_params['competition'][0],
        'latest_round': int(query_params['round'][0]) - 1,
        'year': int(query_params['season'][0])
    }


# should be split into 3 functions and the looping in __main__
def main(competition_code, year, round_num, gcs_bucket):
    # for year in range(min_year, max_year + 1):
    #     for round_num in range(1, max_round + 1):
        try:
            competition = conf.comp_code_to_name(competition_code)
        except (TypeError, KeyError):
            print(f"Unknown Competition Code: {competition_code}")

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

        gcs_client = GCSClient(bucket_name=gcs_bucket)
        gcs_client.upload_to_gcs(
            src_file=str(file_path),
            dest_blob=f"{competition}/match_data/{file_name}"
        )


if __name__ == "__main__":
    load_dotenv('gcp.env')
    env = os.getenv("ENV", "dev")
    if env == 'dev':
        gcs_bucket = os.getenv("DEV_BUCKET")
    else:
        gcs_bucket = os.getenv("PROD_BUCKET")

    next_round_url = get_final_url('https://www.nrl.com/draw/')
    parsed_data = parse_url(next_round_url)

    main(
        competition_code=parsed_data['competition_code'],
        year=parsed_data['year'],
        round_num=parsed_data['latest_round'],
        gcs_bucket=gcs_bucket
    )