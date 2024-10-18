import os
import requests
from googlesearch import search
import time
import random
import logging
from requests.exceptions import HTTPError
import json

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
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)
        logging.info(f"Saved webpage from {url} as {file_path}")
    except Exception as e:
        logging.error(f"Failed to download from {url}: {e}")


def download_first_search_result(query, save_directory):
    logging.info(f"Searching for: {query}")
    try:
        search_results = search(query, num_results=1)
        first_result_url = next(iter(search_results), None)

        if first_result_url:
            file_name = f"result_{query}.html"
            file_path = os.path.join(save_directory, file_name)
            logging.info(f"Downloading from: {first_result_url}")
            save_webpage_content(first_result_url, file_path)
            logging.info(f"Saved as: {file_path}")
        else:
            logging.warning(f"No search results found for query: {query}")
    except HTTPError as e:
        if e.response.status_code == 429:
            logging.error("Rate limit exceeded. Sleeping for 1 hour.")
            time.sleep(3600)
            raise
        else:
            logging.error(f"HTTP error occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred during search: {e}")

    logging.info("Sleeping")
    time.sleep(random.uniform(41, 50))
    logging.info("Woke up")


def save_progress(current_question):
    with open("progress.json", "w") as f:
        json.dump({"last_completed": current_question}, f)


def load_progress():
    try:
        with open("progress.json", "r") as f:
            return json.load(f)["last_completed"]
    except FileNotFoundError:
        return 0


def main():
    base_query = "AWS Certified Data Engineer - Associate exam topics question"
    save_directory = "./html_pages/AWS/data_engineer_associate"
    number_of_questions = 152

    os.makedirs(save_directory, exist_ok=True)

    # start_from = load_progress()
    start_from = 85
    logging.info(f"Resuming from question {start_from + 1}")

    for i in range(start_from + 1, number_of_questions + 1):
        query = f"{base_query} {i} discussion"
        try:
            download_first_search_result(query, save_directory)
            save_progress(i)
        except HTTPError as e:
            if e.response.status_code == 429:
                logging.info(f"Rate limit hit. Stopping at question {i}.")
                break
            else:
                logging.error(f"HTTP error for question {i}: {e}")
        except Exception as e:
            logging.error(f"Error processing question {i}: {e}")


if __name__ == "__main__":
    main()
