import os
import re
import argparse
from loguru import logger
from config import config as conf
import pandas as pd
import duckdb
from utilities.gcs_client import GCSClient


def load_match_data(bucket, blobs):
    dfs = []
    year = -1
    for blob in blobs:
        match = re.search(r"nrl/match_data/(\d{4})_r(\d+)\.json", blob.name)
        try:
            df = pd.read_json(f"gs://{bucket}/{blob.name}")
        except Exception as e:
            logger.info(f"Failed to load blob: {blob.name} | Error: {e}")
        df["year"] = int(match.group(1))
        df["round_num"] = int(match.group(2))
        dfs.append(df)
        if year != int(match.group(1)):
            year = int(match.group(1))
            logger.info(f"Loading {year}")
    df = pd.concat(dfs, axis=0, ignore_index=True)
    return df


def main(gcs_bucket, queries):
    gcs_client = GCSClient(bucket_name=gcs_bucket)
    logger.info("Loading match data from GCS JSON")
    df = load_match_data(bucket=gcs_bucket, blobs=gcs_client.get_blobs())  # noqa: F841

    logger.info("Running feature eng queries")
    for query in queries:
        with open(f"feature_eng/feature_eng/sql/{query}.sql", "r") as f:
            logger.info(f"Creating table: {query}")
            sql_script = f.read()
            duckdb.sql(sql_script)

    logger.info("Saving training data to CSV")
    train_df = duckdb.sql("SELECT * FROM train").df()
    train_df.to_csv("./data/train_df.csv", index=False)
    train_df.to_csv(f"gs://{gcs_bucket}/training/train_df.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        logger.debug("Feature engineering dry run")
    else:
        env = os.getenv("ENV", "dev")
        gcs_bucket = conf.gcs_bucket[env]
        logger.info(f"Set GCS bucket to: {gcs_bucket}")
        main(gcs_bucket, conf.feature_pipeline)
