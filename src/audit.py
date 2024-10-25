import json
from collections import defaultdict
import re


def audit_question_data(data):
    """
    Analyze question data and generate audit statistics
    """
    audit_report = {
        "total_questions": len(data),
        "question_numbers": [],
        "null_count": defaultdict(int),
        "choice_stats": {
            "min_choices": float("inf"),
            "max_choices": 0,
            "avg_choices": 0,
        },
        "voting_stats": {
            "total_votes": 0,
            "questions_with_votes": 0,
            "highest_voted_question": None,
            "highest_vote_count": 0,
        },
        "correct_answer_distribution": defaultdict(int),
    }

    for item in data:
        match = re.search(r"question (\d+)", item["filename"])
        if match:
            audit_report["question_numbers"].append(int(match.group(1)))

        for key, value in item.items():
            if value is None:
                audit_report["null_count"][key] += 1

        num_choices = len(item["choices"])
        audit_report["choice_stats"]["min_choices"] = min(
            audit_report["choice_stats"]["min_choices"], num_choices
        )
        audit_report["choice_stats"]["max_choices"] = max(
            audit_report["choice_stats"]["max_choices"], num_choices
        )

        audit_report["correct_answer_distribution"][item["correct_answer"]] += 1

        total_votes_for_question = sum(vote["vote_count"] for vote in item["user_data"])
        audit_report["voting_stats"]["total_votes"] += total_votes_for_question

        if total_votes_for_question > 0:
            audit_report["voting_stats"]["questions_with_votes"] += 1

        if (
            total_votes_for_question
            > audit_report["voting_stats"]["highest_vote_count"]
        ):
            audit_report["voting_stats"][
                "highest_vote_count"
            ] = total_votes_for_question
            audit_report["voting_stats"]["highest_voted_question"] = item["filename"]

    audit_report["choice_stats"]["avg_choices"] = len(data[0]["choices"]) if data else 0
    audit_report["question_numbers"].sort()
    return audit_report


def main():
    try:
        with open("./questions/AWS/data_engineer_associate.json", "r") as file:
            data = json.load(file)

        audit_report = audit_question_data(data)

        with open("audit_report.json", "w") as f:
            json.dump(audit_report, f, indent=4)

        print("\n=== Question Data Audit Report ===")
        print(f"Total Questions: {audit_report['total_questions']}")
        print(f"Question Numbers Found: {audit_report['question_numbers']}")
        print("\nNull Values Found:")
        for field, count in audit_report["null_count"].items():
            print(f"  {field}: {count}")
        print("\nChoice Statistics:")
        print(f"  Minimum Choices: {audit_report['choice_stats']['min_choices']}")
        print(f"  Maximum Choices: {audit_report['choice_stats']['max_choices']}")
        print(f"  Average Choices: {audit_report['choice_stats']['avg_choices']}")
        print("\nVoting Statistics:")
        print(f"  Total Votes: {audit_report['voting_stats']['total_votes']}")
        print(
            f"  Questions with Votes: {audit_report['voting_stats']['questions_with_votes']}"
        )
        print(
            f"  Most Voted Question: {audit_report['voting_stats']['highest_voted_question']}"
        )
        print(
            f"  Highest Vote Count: {audit_report['voting_stats']['highest_vote_count']}"
        )
        print("\nCorrect Answer Distribution:")
        for answer, count in audit_report["correct_answer_distribution"].items():
            print(f"  Option {answer}: {count}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
