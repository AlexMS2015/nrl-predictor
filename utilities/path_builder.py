from pathlib import Path


class PathBuilder:
    def __init__(self, bucket):
        self.bucket = bucket
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def match_filename(self, round_num, year):
        return f"{year}_r{round_num}.json"

    def blob_path(self, *parts):
        return "/".join(parts)

    def gcs_path(self, blob_path):
        return f"gs://{self.bucket}/{blob_path}"

    def local_path(self, blob_path):
        local_path = self.data_dir / blob_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        return str(local_path)

    # ---- High-level helpers ----
    # def local_match_path(self, competition, year, round_num):
    #     """Full local path for a match JSON file."""
    #     file_name = self.match_filename(round_num, year)
    #     blob = self.blob_path(competition, "match", file_name)
    #     p = self.local_path(blob)
    #     p.parent.mkdir(parents=True, exist_ok=True)
    #     return p

    # def gcs_match_path(self, competition, year, round_num):
    #     """Blob path for GCS upload (relative to bucket)."""
    #     file_name = self.match_filename(round_num, year)
    #     return self.blob_path(competition, "match", file_name)
