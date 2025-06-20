# import json
# import pandas as pd
# import numpy as np
# from utilities.get_detailed_match_data import get_detailed_nrl_data
# from utilities.set_up_driver import set_up_driver
# from pathlib import Path


# driver = set_up_driver()

# data = get_detailed_nrl_data(
#     round=1,
#     year=2025,
#     home_team='raiders',
#     away_team='warriors',
#     driver=driver,
#     nrl_website='https://www.nrl.com/draw/nrl-premiership/'
# )
# print(data)

# # root = Path(".")

from google.cloud import storage

client = storage.Client(project='watchful-slice-463402-m4')
bucket = client.bucket('nrl-data-dev')

# Check bucket details
try:
    bucket.reload()
    print(f"Bucket project number: {bucket.project_number}")
    print(f"Bucket location: {bucket.location}")
    print(f"Client project: {client.project}")
except Exception as e:
    print(f"Error accessing bucket: {e}")