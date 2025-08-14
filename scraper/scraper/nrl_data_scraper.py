import os
import json
import time
import requests
from loguru import logger
from config import conf
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


class NRLDataScraper:
    driver = None

    def __init__(self, competition_code, round=None, year=None):
        if NRLDataScraper.driver is None:
            NRLDataScraper.driver = NRLDataScraper._set_up_driver()
        self.driver = NRLDataScraper.driver

        if not all((round, year)):
            logger.info("Getting most recent round and year")
            draw_url = conf.urls.draw_url(competition_code)
            next_round_url = self._get_final_url(draw_url)
            competition_code, year, round = self._parse_url(next_round_url)

        self.competition_code = competition_code
        self.competition = conf.comp_code_to_name(competition_code)
        self.round = round
        self.year = year
        self.round_url = conf.urls.round_url(competition_code, round, year)

    @classmethod
    def _set_up_driver(cls):
        in_docker = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

        options = Options()

        if not in_docker:
            # Automatically install the Chrome driver if not already installed
            chromedriver_autoinstaller.install()

        if in_docker:
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")

        # Ignore annoying messages from the NRL website
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless=new")
        options.add_argument("log-level=3")

        # Exclude logging to assist with errors caused by NRL website
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=options)
        return driver

    @logger.catch
    def _get_final_url(self, draw_url, retries=3):
        logger.info(f"Getting final url for: {draw_url}")
        for i in range(retries):
            try:
                self.driver.get(draw_url)
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )
                logger.info(f"Final url: {self.driver.current_url}")
                return self.driver.current_url
            except Exception as e:
                logger.critical(f"Cannot obtain final URL | Retry: {i} | Error: {e}")
                time.sleep(5)
            # finally:
            #     self.driver.quit()

    def _parse_url(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        try:
            competition_code = query_params["competition"][0]
            year = query_params["season"][0]
            round = str(int(query_params["round"][0]) - 1)
        except (KeyError, IndexError, ValueError) as e:
            logger.critical(f"Cannot extract comp, year, round: {e}")
            raise e

        return competition_code, year, round

    def get_basic_match_data(self):
        logger.info(
            f"Fetching data for comp={self.competition_code} year={self.year}, round={self.round}"
        )

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(self.round_url, headers=headers)
        if response.status_code != 200:
            logger.critical("Failed to fetch data")
            raise RuntimeError("Failed to fetch data")

        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("div", {"id": "vue-draw"})
        if not script_tag:
            logger.critical("Could not find fixture data")
            raise RuntimeError("Could not find fixture data")
        raw_json = script_tag["q-data"]
        raw_json = raw_json.replace("&quot;", '"')  # Fix encoding
        data = json.loads(raw_json)
        fixtures = data.get("fixtures", [])

        matches_json = []
        for fixture in fixtures:
            if fixture["type"] == "Match":
                match = {
                    "year": self.year,
                    "round_num": self.round,
                    "round": fixture["roundTitle"],
                    "home": fixture["homeTeam"]["nickName"],
                    "home_score": fixture["homeTeam"].get("score", 0),
                    "away": fixture["awayTeam"]["nickName"],
                    "away_score": fixture["awayTeam"].get("score", 0),
                    "venue": fixture["venue"],
                    "date": fixture["clock"]["kickOffTimeLong"],
                    "match_centre_uRL": f"https://www.nrl.com{fixture['matchCentreUrl']}",
                }
                matches_json.append(match)

        return matches_json
