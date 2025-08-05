from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
from loguru import logger
import json
import time


@logger.catch
def get_final_url(driver, url, retries=3):
    for i in range(retries):
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return driver.current_url
        except Exception as e:
            logger.critical(f"Cannot obtain final URL | Retry: {i} | Error: {e}")
            time.sleep(5)
        finally:
            driver.quit()


def parse_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    try:
        competition_code = query_params["competition"][0]
        year = int(query_params["season"][0])
        round_num = int(query_params["round"][0]) - 1
    except (KeyError, IndexError, ValueError) as e:
        logger.critical("Cannot extract comp, year, round:", e)
        raise e

    return competition_code, year, round_num


def save_locally(match_json, competition, year, round_num):
    root_dir = Path(__file__).parents[2]
    data_dir = root_dir / "data" / competition / "match_data"
    data_dir = data_dir.resolve()  # convert to absolute path
    data_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{year}_r{round_num}.json"
    file_path = data_dir / file_name
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(match_json, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.warning(f"Error writing file: {e}")

    return file_path, file_name
