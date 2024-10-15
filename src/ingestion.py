import os
import requests
from googlesearch import search
import time
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logfile.log"), logging.StreamHandler()],
)


def save_webpage_content(url, file_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        with open(file_path, "wb") as file:
            file.write(response.content)
        logging.info(f"Saved webpage from {url} as {file_path}")
    except Exception as e:
        logging.error(f"Failed to download from {url}: {e}")


def download_first_search_result(query, save_directory):
    logging.info(f"Searching for: {query}")
    search_results = search(query, num_results=1)
    first_result_url = next(iter(search_results), None)

    if first_result_url:
        file_name = f"result_{query}.html"
        file_path = os.path.join(save_directory, file_name)
        logging.info(f"Downloading from: {first_result_url}")
        save_webpage_content(first_result_url, file_path)
        logging.info(f"Saved as: {file_path}")

        logging.info("Sleeping")
        time.sleep(random.uniform(20, 31))
        logging.info("Woke up")


def main():
    base_query = "Amazon AWS Certified Data Engineer - Associate question"
    save_directory = "./html_pages/aws_test"
    number_of_questions = 3

    os.makedirs(save_directory, exist_ok=True)

    for i in range(1, number_of_questions + 1):
        query = f"{base_query} {i} discussion"
        download_first_search_result(query, save_directory)


if __name__ == "__main__":
    main()
