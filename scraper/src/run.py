"""
Script to run the data scraper for match and player data.
"""

import os
from loguru import logger
from dotenv import load_dotenv
from config import config as conf
from utilities.gcs_client import GCSClient
from scraper.src.utilities.scraper_functions import get_basic_match_data
from scraper.src.utilities.set_up_driver import set_up_driver
from scraper.src.utilities.utils import get_final_url, parse_url, save_locally


def main(gcs_bucket):
    driver = set_up_driver()
    next_round_url = get_final_url(driver, "https://www.nrl.com/draw/")
    logger.info(f"URL: {next_round_url}")

    competition_code, year, round_num = parse_url(next_round_url)
    competition = conf.comp_code_to_name(competition_code)
    logger.info(f"Fetching data for {competition} {year}, {round_num}...")

    match_json = get_basic_match_data(round_num, year, competition_code)
    file_path, file_name = save_locally(match_json, competition, year, round_num)
    gcs_client = GCSClient(bucket_name=gcs_bucket)
    gcs_client.upload_to_gcs(
        src_file=str(file_path), dest_blob=f"{competition}/match_data/{file_name}"
    )


if __name__ == "__main__":
    load_dotenv("gcp.env")
    env = os.getenv("ENV", "dev")
    gcs_bucket = os.getenv("DEV_BUCKET")
    if env == "prod":
        gcs_bucket = os.getenv("PROD_BUCKET")
