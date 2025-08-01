"""
Module to set up Chrome Web Driver for Scalping.

This module provides a function to set up the Chrome Web Driver with specific options
for automated web scraping tasks related to Scalping.
"""

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


def set_up_driver():
    """Set up the Chrome Web Driver for Scalping.

    This function sets up the Chrome Web Driver with specified options.

    :return: WebDriver object for Chrome
    """
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
