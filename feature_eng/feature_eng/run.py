import argparse
from loguru import logger
from config import conf
import pandas as pd
import duckdb


def load_match_data(blobs, bucket="nrl-data-dev"):
    dfs = []
    year = -1
    for blob in blobs:
        try:
            df = pd.read_json(f"gs://{bucket}/{blob.name}")
        except Exception as e:
            logger.info(f"Failed to load blob: {blob.name} | Error: {e}")
        dfs.append(df)
        if year != df.year[0]:
            year = df.year[0]
            logger.info(f"Loading {year}")
    df = pd.concat(dfs, axis=0, ignore_index=True)
    return df


def main(competition, queries, local_run):
    logger.info("Loading match data from GCS JSON")
    blob = conf.paths.blob_path(competition, "match")
    blobs = conf.gcs_client.get_blobs(blob)
    if local_run:
        blobs = [blob for blob in blobs][:2]
    df = load_match_data(blobs=blobs)  # noqa: F841

    logger.info("Running feature eng queries")
    for query in queries:
        with open(f"feature_eng/feature_eng/sql/{query}.sql", "r") as f:
            logger.info(f"Creating table: {query}")
            sql_script = f.read()
            duckdb.sql(sql_script)

    logger.info("Saving training data to CSV")
    train_df = duckdb.sql("SELECT * FROM train").df()
    file_name = "train_df.csv"
    blob_path = conf.paths.blob_path("training", file_name)
    local_path = conf.paths.local_path(blob_path)
    train_df.to_csv(local_path, index=False)
    conf.gcs_client.upload_to_gcs(
        src_file=local_path,
        dest_blob=blob_path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--local-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        logger.debug("Feature engineering dry run")
    else:
        competition = conf.comp_code_to_name("111")
        main(competition, conf.feature_pipeline, local_run=args.local_run)
