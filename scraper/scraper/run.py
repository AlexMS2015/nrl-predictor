"""
Script to run the data scraper for match and player data.
"""

import argparse
from loguru import logger
from config import paths
from utilities.gcs_client import gcs_client
from scraper.nrl_data_scraper import NRLDataScraper
import json


def save_locally(path, data_json):
    logger.info(f"Saving data to: {path}")
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data_json, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.warning(f"Error writing file: {e}")


def main(competition_code):
    scraper = NRLDataScraper(competition_code=competition_code)
    match_json = scraper.get_basic_match_data()

    file_name = paths.match_filename(scraper.round, scraper.year)
    blob_path = paths.blob_path(scraper.competition, "match", file_name)
    local_path = paths.local_path(blob_path)

    save_locally(local_path, match_json)
    gcs_client.upload_to_gcs(
        src_file=str(local_path),
        dest_blob=blob_path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        logger.debug("Scraper dry run")
    else:
        # for competition_code in conf.competition_codes:
        # logger.info(f"Fetching match data for {competition_code}")
        competition_code = "111"
        main(competition_code)
