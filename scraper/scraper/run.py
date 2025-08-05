"""
Script to run the data scraper for match and player data.
"""

import os
from dotenv import load_dotenv
from loguru import logger
from config import config as conf
from utilities.gcs_client import GCSClient
from scraper.utilities.scraper_functions import get_basic_match_data
from scraper.utilities.set_up_driver import set_up_driver
from scraper.utilities.utils import get_final_url, parse_url, save_locally
from pathlib import Path


def main(gcs_bucket):
    driver = set_up_driver()
    next_round_url = get_final_url(driver, "https://www.nrl.com/draw/")
    competition_code, year, round_num = parse_url(next_round_url)
    competition = conf.comp_code_to_name(competition_code)
    match_json = get_basic_match_data(round_num, year, competition_code)
    file_path, file_name = save_locally(match_json, competition, year, round_num)
    gcs_client = GCSClient(bucket_name=gcs_bucket)
    gcs_client.upload_to_gcs(
        src_file=str(file_path), dest_blob=f"{competition}/match_data/{file_name}"
    )


if __name__ == "__main__":
    env_path = Path(__file__).parents[2] / "gcp.env"
    load_dotenv(env_path)
    env = os.getenv("ENV", "dev")
    gcs_bucket = os.getenv("DEV_BUCKET")
    if env == "prod":
        gcs_bucket = os.getenv("PROD_BUCKET")
    logger.info(f"Set GCS bucket to: {gcs_bucket}")

    main(gcs_bucket)
