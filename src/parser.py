from bs4 import BeautifulSoup
import os
import json

html_dir = "./html_pages/terraform/terraform_associate"
extracted_data = []

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            html = file.read()

    soup = BeautifulSoup(html, "html.parser")

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

    data = {
        "filename": filename,
        "question": question,
        "choices": choices,
        "correct_answer": correct_answer,
        "user_data": user_data,
    }

    extracted_data.append(data)

output_file = "./questions/terraform_associate_new.json"
with open(output_file, "w") as json_file:
    json.dump(extracted_data, json_file, indent=4)
