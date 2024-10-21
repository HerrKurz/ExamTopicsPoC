from bs4 import BeautifulSoup
import os
import json
import chardet
import html
import unicodedata


PATH_EXAM = "Azure/DP_900"
html_dir = f"./html_pages/{PATH_EXAM}"
extracted_data = []


def detect_encoding(file_path):
    with open(file_path, "rb") as file:
        raw_data = file.read()
    return chardet.detect(raw_data)["encoding"]


def normalize_text(text):
    if text is None:
        return None
    text = html.unescape(text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text


for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        encoding = detect_encoding(file_path)

        try:
            with open(file_path, "r", encoding=encoding) as file:
                html_content = file.read()
        except UnicodeDecodeError:
            print(
                f"Failed to decode {filename} with detected encoding {encoding}. Skipping this file."
            )
            continue

        soup = BeautifulSoup(html_content, "html.parser")

        question_div = soup.find("div", class_="question-body")
        question = (
            question_div.find("p", class_="card-text").get_text(strip=True)
            if question_div
            else None
        )

        choices = []
        choices_div = soup.find("div", class_="question-choices-container")
        if choices_div:
            list_items = choices_div.find_all("li", class_="multi-choice-item")
            choices = [item.get_text(strip=True) for item in list_items]

        correct_answer_span = soup.find("span", class_="correct-answer")
        correct_answer = (
            correct_answer_span.get_text(strip=True) if correct_answer_span else None
        )

        voted_answers_div = soup.find("div", class_="voted-answers-tally d-none")
        user_data = None
        if voted_answers_div:
            script_tag = voted_answers_div.find("script", type="application/json")
            if script_tag:
                user_data = json.loads(script_tag.string)

        question = normalize_text(question)
        choices = [normalize_text(choice) for choice in choices]
        correct_answer = normalize_text(correct_answer)

        data = {
            "filename": filename,
            "question": question,
            "choices": choices,
            "correct_answer": correct_answer,
            "user_data": user_data,
        }

        extracted_data.append(data)

output_file = f"./questions/{PATH_EXAM}.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(extracted_data, json_file, indent=4, ensure_ascii=True)

print(f"Data extraction complete. Output saved to {output_file}")
