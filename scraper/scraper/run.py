"""
Script to run the data scraper for match and player data.
"""

import os
import argparse
from loguru import logger
from config import config as conf
from utilities.gcs_client import GCSClient
from scraper.utilities.scraper_functions import get_basic_match_data
from scraper.utilities.set_up_driver import set_up_driver
from scraper.utilities.utils import get_final_url, parse_url, save_locally


def main(gcs_bucket, competition_code):
    driver = set_up_driver()
    next_round_url = get_final_url(driver, conf.draw_link(competition_code))
    competition_code, year, round_num = parse_url(next_round_url)
    competition = conf.comp_code_to_name(competition_code)
    match_json = get_basic_match_data(round_num, year, competition_code)
    file_path, file_name = save_locally(match_json, competition, year, round_num)
    gcs_client = GCSClient(bucket_name=gcs_bucket)
    gcs_client.upload_to_gcs(
        src_file=str(file_path),
        dest_blob=f"{competition}/{conf.blobs['match']}/{file_name}",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        logger.debug("Scraper dry run")
    else:
        env = os.getenv("ENV", "dev")
        gcs_bucket = conf.gcs_bucket[env]
        logger.info(f"Set GCS bucket to: {gcs_bucket}")
        # for competition_code in conf.competition_codes:
        # logger.info(f"Fetching match data for {competition_code}")
        competition_code = "111"
        main(gcs_bucket, competition_code)
